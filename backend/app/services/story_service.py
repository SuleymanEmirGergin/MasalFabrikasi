import os
import os
from openai import AsyncOpenAI
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    pipeline = None
from app.core.config import settings
from app.services.tts_service import TTSService
from app.services.search_service import SearchService
from app.core.resilience import openai_circuit_breaker, retry_on_failure


from app.services.wiro_client import wiro_client

class StoryService:
    def __init__(self):
        self.draft_client = None
        self.final_client = None
        
        # Draft Client (Gemini Flash via Wiro or Google)
        if settings.GEMINI_API_KEY:
            self.draft_client = AsyncOpenAI(
                api_key=settings.GEMINI_API_KEY, 
                base_url=settings.GPT_BASE_URL if "wiro" in settings.GPT_BASE_URL else "https://generativelanguage.googleapis.com/v1beta/openai/"
            )
            
        # Final Story Client (Standard OpenAI compatible)
        if settings.GPT_API_KEY:
            self.final_client = AsyncOpenAI(
                api_key=settings.GPT_API_KEY,
                base_url=settings.GPT_BASE_URL
            )
        
        # Fallback for search/legacy if needed
        self.openai_client = self.final_client or self.draft_client

    @openai_circuit_breaker.call
    @retry_on_failure(max_retries=2, delay=1.0)
    async def generate_draft(self, prompt: str) -> str:
        """Taslak veya fikir üretimi için hızlı Gemini modelini kullanır."""
        if not self.draft_client:
            return "Draft client not configured."
        
        try:
            response = await self.draft_client.chat.completions.create(
                model=settings.GEMINI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Draft generation error: {e}")
            return "Draft generation failed."

    @retry_on_failure(max_retries=2, delay=2.0)
    async def generate_story(
        self, 
        theme: str, 
        language: str = "tr", 
        story_type: str = "masal",
        creativity: float = 0.8,
        pacing: str = "medium",
        perspective: str = "third",
        vocabulary: str = "normal"
    ) -> str:
        """
        Final hikaye üretimi için GPT-OSS (Wiro) kullanır.
        Uses WiroClient run_and_wait for robust long-running generation.
        """
        prompt = self._create_prompt(theme, language, story_type, pacing, perspective, vocabulary)
        
        # If it's Wiro OSS model, use the specialized WiroClient
        if "gpt-oss" in settings.GPT_MODEL.lower():
            try:
                inputs = {
                    "prompt": prompt,
                    "system_prompt": "Sen usta bir hikaye yazarısın.",
                    "temperature": str(creativity),
                    "top_p": "0.95",
                    "max_tokens": "0" # Wiro default
                }
                # openai/gpt-oss-20b -> provider=openai, model=gpt-oss-20b
                parts = settings.GPT_MODEL.split("/")
                provider = parts[0] if len(parts) > 1 else "openai"
                model_slug = parts[1] if len(parts) > 1 else parts[0]

                result = await wiro_client.run_and_wait(provider, model_slug, inputs, is_json=True)
                
                # Extract output from Wiro response
                detail = result.get("detail", {})
                if detail and detail.get("tasklist"):
                    # Check debugoutput or results (Wiro detail structure varies)
                    # Based on user documentation, outputs might be files or text in debugoutput
                    return detail["tasklist"][0].get("debugoutput", "").strip() or "Story generation completed but no output text found."
            except Exception as e:
                print(f"Wiro GPT-OSS generation error: {e}")

        # Fallback to standard OpenAI client if WiroClient fails or model is different
        if self.final_client:
            try:
                response = await self.final_client.chat.completions.create(
                    model=settings.GPT_MODEL,
                    messages=[
                        {"role": "system", "content": "Sen usta bir hikaye yazarısın."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=2000,
                    temperature=creativity
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"Standard story generation error: {e}")
        
        # Fallback to draft if final fails
        if self.draft_client:
            return await self.generate_draft(prompt)
            
        return self._generate_fallback_story(theme, language)
    
    def _create_prompt(
        self, 
        theme: str, 
        language: str, 
        story_type: str = "masal",
        pacing: str = "medium",
        perspective: str = "third",
        vocabulary: str = "normal"
    ) -> str:
        """Hikâye üretimi için prompt oluşturur."""
        # Hikâye türüne göre stil belirle
        story_type_descriptions = {
            "masal": "masal tarzında, büyülü ve ders verici",
            "bilimkurgu": "bilimkurgu tarzında, gelecekçi ve teknolojik",
            "korku": "korku tarzında, gerilimli ve ürkütücü",
            "macera": "macera tarzında, heyecanlı ve aksiyon dolu",
            "romantik": "romantik tarzında, duygusal ve aşk dolu",
            "komedi": "komedi tarzında, eğlenceli ve mizahi",
            "dram": "dram tarzında, duygusal ve derin",
            "fantastik": "fantastik tarzında, büyülü ve olağanüstü"
        }
        
        type_desc = story_type_descriptions.get(story_type, "yaratıcı")
        
        # Advanced Settings Instructions
        pacing_instr = {
            "slow": "Hikayeyi yavaş ve detaylı bir tempoda anlat. Karakterlerin duygularına ve çevre tasvirlerine odaklan.",
            "medium": "Hikayeyi dengeli bir tempoda anlat.",
            "fast": "Hikayeyi hızlı ve aksiyon odaklı bir tempoda anlat. Olaylar hızlı gelişsin."
        }.get(pacing, "Dengeli bir tempo kullan.")
        
        perspective_instr = {
            "first": "Hikayeyi birinci şahıs (ben dili) bakış açısıyla anlat.",
            "third": "Hikayeyi üçüncü şahıs (o dili) bakış açısıyla anlat."
        }.get(perspective, "Üçüncü şahıs bakış açısı kullan.")
        
        vocab_instr = {
            "simple": "Basit, anlaşılır ve kısa cümleler kullan. Çocukların anlayabileceği bir dil olsun.",
            "normal": "Akıcı ve doğal bir dil kullan.",
            "complex": "Zengin, edebi ve betimleyici bir dil kullan. Karmaşık cümle yapıları ve geniş bir kelime dağarcığı kullan."
        }.get(vocabulary, "Doğal bir dil kullan.")

        if language == "tr":
            return f"""Aşağıdaki temaya göre {type_desc} bir hikâye yaz. 
Hikâye 3-5 paragraf uzunluğunda olsun ve bir başlangıç, gelişme ve sonuç içersin.

Ayarlar:
- Tür: {story_type}
- Tempo: {pacing_instr}
- Bakış Açısı: {perspective_instr}
- Dil Seviyesi: {vocab_instr}

Tema: {theme}

Hikâye:"""
        else:
            type_desc_en = {
                "masal": "fairy tale style, magical and moral",
                "bilimkurgu": "science fiction style, futuristic and technological",
                "korku": "horror style, suspenseful and scary",
                "macera": "adventure style, exciting and action-packed",
                "romantik": "romantic style, emotional and love-filled",
                "komedi": "comedy style, fun and humorous",
                "dram": "drama style, emotional and deep",
                "fantastik": "fantasy style, magical and extraordinary"
            }.get(story_type, "creative")
            
            pacing_instr_en = {
                "slow": "Tell the story at a slow and detailed pace. Focus on character emotions and environmental descriptions.",
                "medium": "Tell the story at a balanced pace.",
                "fast": "Tell the story at a fast and action-oriented pace. Events should unfold quickly."
            }.get(pacing, "Use a balanced pace.")

            perspective_instr_en = {
                "first": "Tell the story from a first-person perspective (I).",
                "third": "Tell the story from a third-person perspective (He/She/They)."
            }.get(perspective, "Use third-person perspective.")

            vocab_instr_en = {
                "simple": "Use simple, clear, and short sentences. Use language suitable for children.",
                "normal": "Use fluent and natural language.",
                "complex": "Use rich, literary, and descriptive language. Use complex sentence structures and a wide vocabulary."
            }.get(vocabulary, "Use natural language.")
            
            return f"""Write a {type_desc_en} story based on the following theme.
The story should be 3-5 paragraphs long and include a beginning, development, and conclusion.

Settings:
- Type: {story_type}
- Pacing: {pacing_instr_en}
- Perspective: {perspective_instr_en}
- Language Level: {vocab_instr_en}

Theme: {theme}

Story:"""
    
    async def _generate_with_openai(self, prompt: str, temperature: float = 0.8) -> str:
        """OpenAI API ile hikâye üretir."""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sen yaratıcı bir hikâye yazarısın. Kullanıcının verdiği temaya ve ayarlara göre ilgi çekici hikâyeler yazarsın."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI API hatası: {e}")
            return self._generate_fallback_story(prompt, "tr")
    
    async def _generate_with_huggingface(self, prompt: str) -> str:
        """Hugging Face modeli ile hikâye üretir."""
        try:
            result = self.hf_pipeline(
                prompt,
                max_length=500,
                num_return_sequences=1,
                temperature=0.8,
                do_sample=True
            )
            return result[0]['generated_text'].replace(prompt, "").strip()
        except Exception as e:
            print(f"Hugging Face model hatası: {e}")
            return self._generate_fallback_story(prompt, "tr")
    
    def _generate_fallback_story(self, theme: str, language: str) -> str:
        """API'ler çalışmazsa basit bir hikâye döner."""
        if language == "tr":
            return f"""Bir zamanlar, {theme} hakkında harika bir hikâye vardı.

Bu hikâyede, karakterlerimiz maceralı bir yolculuğa çıktılar. Yolda birçok zorlukla karşılaştılar ama asla pes etmediler.

Sonunda, tüm çabalarının karşılığını aldılar ve mutlu bir sonla hikâyeleri tamamlandı. Bu hikâye, cesaret ve azmin gücünü gösteriyordu."""
        else:
            return f"""Once upon a time, there was a wonderful story about {theme}.

In this story, our characters embarked on an adventurous journey. They faced many challenges along the way but never gave up.

In the end, they reaped the rewards of all their efforts and their story ended with a happy ending. This story showed the power of courage and determination."""
    
    async def generate_plot_twist(
        self,
        story_text: str,
        language: str = "tr"
    ) -> str:
        """
        Hikâyeye plot twist ekler.
        
        Args:
            story_text: Mevcut hikâye metni
            language: Dil
        
        Returns:
            Plot twist metni
        """
        if language == "tr":
            prompt = f"""Aşağıdaki hikâyeye sürpriz bir plot twist ekle. Plot twist hikâyeyi tamamen değiştirmeli ve okuyucuyu şaşırtmalı.

Mevcut Hikâye:
{story_text}

Plot twist'i hikâyenin sonuna ekle ve hikâyeyi yeniden yaz. Plot twist mantıklı olmalı ama beklenmedik olmalı."""
        else:
            prompt = f"""Add a surprising plot twist to the following story. The plot twist should completely change the story and surprise the reader.

Current Story:
{story_text}

Add the plot twist to the end of the story and rewrite it. The plot twist should be logical but unexpected."""
        
        try:
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Sen yaratıcı bir hikâye yazarısın. Sürpriz plot twist'ler ekleyerek hikâyeleri daha ilgi çekici hale getirirsin."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.9
                )
                return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Plot twist üretim hatası: {e}")
        
        # Fallback
        if language == "tr":
            return f"{story_text}\n\nAma aslında, hiçbir şey göründüğü gibi değildi..."
        else:
            return f"{story_text}\n\nBut actually, nothing was as it seemed..."
    
    async def generate_alternative_ending(
        self,
        story_text: str,
        ending_type: str = "surprise",
        language: str = "tr"
    ) -> str:
        """
        Hikâye için alternatif son üretir.
        
        Args:
            story_text: Mevcut hikâye metni
            ending_type: Son türü (surprise, happy, sad, open)
            language: Dil
        
        Returns:
            Alternatif son metni
        """
        ending_types = {
            "surprise": "sürpriz bir son",
            "happy": "mutlu bir son",
            "sad": "üzücü bir son",
            "open": "açık uçlu bir son",
        }
        
        if language == "tr":
            ending_desc = ending_types.get(ending_type, "farklı bir son")
            prompt = f"""Aşağıdaki hikâye için {ending_desc} yaz. Hikâyenin sonunu değiştir ama başlangıç ve gelişme kısmını koru.

Mevcut Hikâye:
{story_text}

Lütfen sadece son kısmı (1-2 paragraf) yeniden yaz ve alternatif sonu ekle."""
        else:
            ending_types_en = {
                "surprise": "a surprising ending",
                "happy": "a happy ending",
                "sad": "a sad ending",
                "open": "an open-ended ending",
            }
            ending_desc = ending_types_en.get(ending_type, "a different ending")
            prompt = f"""Write {ending_desc} for the following story. Change the ending but keep the beginning and development parts.

Current Story:
{story_text}

Please rewrite only the ending part (1-2 paragraphs) and add the alternative ending."""
        
        try:
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Sen yaratıcı bir hikâye yazarısın. Hikâyeler için farklı sonlar yazarsın."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.8
                )
                return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Alternatif son üretim hatası: {e}")
        
        # Fallback
        if language == "tr":
            return f"{story_text}\n\nAma belki de hikâye farklı bir şekilde sonlanabilirdi..."
        else:
            return f"{story_text}\n\nBut perhaps the story could have ended differently..."
    
    async def continue_story(
        self,
        story_text: str,
        continuation_length: str = "medium",
        language: str = "tr"
    ) -> str:
        """
        Mevcut hikâyeyi devam ettirir.
        
        Args:
            story_text: Mevcut hikâye metni
            continuation_length: Devam uzunluğu (short, medium, long)
            language: Dil
        
        Returns:
            Devam eden hikâye metni
        """
        length_descriptions = {
            "short": "1-2 paragraf",
            "medium": "2-3 paragraf",
            "long": "3-5 paragraf",
        }
        
        if language == "tr":
            length_desc = length_descriptions.get(continuation_length, "2-3 paragraf")
            prompt = f"""Aşağıdaki hikâyeyi doğal bir şekilde devam ettir. Hikâyenin tonunu ve stilini koru.

Mevcut Hikâye:
{story_text}

Lütfen hikâyeyi {length_desc} uzunluğunda devam ettir. Hikâyenin akışını bozmadan, mantıklı bir şekilde ilerlet."""
        else:
            length_descriptions_en = {
                "short": "1-2 paragraphs",
                "medium": "2-3 paragraphs",
                "long": "3-5 paragraphs",
            }
            length_desc = length_descriptions_en.get(continuation_length, "2-3 paragraphs")
            prompt = f"""Continue the following story naturally. Maintain the tone and style of the story.

Current Story:
{story_text}

Please continue the story for {length_desc}. Progress it logically without breaking the flow."""
        
        try:
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Sen yaratıcı bir hikâye yazarısın. Mevcut hikâyeleri doğal ve akıcı bir şekilde devam ettirirsin."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=800,
                    temperature=0.8
                )
                continuation = response.choices[0].message.content.strip()
                return f"{story_text}\n\n{continuation}"
        except Exception as e:
            print(f"Hikâye devam ettirme hatası: {e}")
        
        # Fallback
        if language == "tr":
            return f"{story_text}\n\nVe böylece hikâye devam etti..."
        else:
            return f"{story_text}\n\nAnd so the story continued..."
    
    async def generate_bedtime_story(
        self,
        theme: str = "rahatlatıcı bir gece masalı",
        language: str = "tr",
        age_group: str = "3-6"  # 3-6, 7-10, 11+
    ) -> str:
        """
        Uyku öncesi için özel olarak tasarlanmış sakinleştirici hikaye üretir.
        
        Bedtime Story Özellikleri:
        - Yavaş tempo ve rahatlatıcı ton
        - Basit, anlaşılır kelimeler
        - Pozitif ve güvenli sonlar
        - Stressiz, barışçıl içerik
        - Tahmin edilebilir yapı (çocukları rahatlatır)
        
        Args:
            theme: Hikaye teması (varsayılan sakinleştirici)
            language: Dil
            age_group: Yaş grubu (kelime seçimini etkiler)
        
        Returns:
            Uyku masalı metni
        """
        # Bedtime presets
        creativity = 0.6  # Daha tahmin edilebilir, rahatlatıcı
        pacing = "slow"  # Yavaş, detaylı
        perspective = "third"  # Genelde 3. şahıs daha rahatlatıcı
        
        # Yaş grubuna göre vocabulary
        vocab_map = {
            "3-6": "simple",
            "7-10": "normal",
            "11+": "normal"
        }
        vocabulary = vocab_map.get(age_group, "simple")
        
        # Bedtime-specific prompt enhancement
        bedtime_theme = self._enhance_bedtime_theme(theme, language, age_group)
        
        return await self.generate_story(
            theme=bedtime_theme,
            language=language,
            story_type="masal",  # Fairy tales are best for bedtime
            creativity=creativity,
            pacing=pacing,
            perspective=perspective,
            vocabulary=vocabulary
        )
    
    def _enhance_bedtime_theme(self, theme: str, language: str, age_group: str) -> str:
        """Bedtime hikaye temasını rahatlatıcı öğelerle zenginleştirir."""
        if language == "tr":
            bedtime_elements = [
                "Hikaye sakinleştirici ve rahatlatıcı olmalı.",
                "Güvenli ve sıcak bir atmosfer yaratmalı.",
                "Pozitif duygular uyandırmalı.",
                "Sonunda herkes mutlu ve huzurlu olmalı.",
                "Uykuya hazırlayıcı yumuşak bir ton kullanmalı."
            ]
            enhanced = f"{theme}\n\nÖzel İstekler:\n" + "\n".join([f"- {e}" for e in bedtime_elements])
        else:
            bedtime_elements = [
                "The story should be calming and soothing.",
                "Create a safe and warm atmosphere.",
                "Evoke positive emotions.",
                "Everyone should be happy and peaceful at the end.",
                "Use a soft tone that prepares for sleep."
            ]
            enhanced = f"{theme}\n\nSpecial Requirements:\n" + "\n".join([f"- {e}" for e in bedtime_elements])
        
        return enhanced

