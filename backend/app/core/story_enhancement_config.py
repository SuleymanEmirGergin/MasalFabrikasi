# Auto-generated configuration for Story Enhancement Services
# This file replaces hundreds of individual service files.

STORY_ENHANCEMENT_CONFIG = {
    "wizard": {
        "system_role": "Sen bir çocuk hikayesi yazarısın.",
        "prompt_template": "Aşağıdaki bilgilere göre bir {session.get('style', 'masal')} hikayesi yaz:\n\nTema: {session.get('theme', '')}\nKarakterler: {', '.join(session.get('characters', []))}\nMekan: {session.get('setting', '')}\nOlay Örgüsü: {session.get('plot_points', [''])[0]}\nUzunluk: {session.get('length', 'orta')}\n\nHikayeyi Türkçe olarak yaz ve çocuklar için uygun bir dil kullan."
    },
    "refinement": {
        "system_role": "Sen bir i̇ncelik uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi i̇ncelik açısından iyileştir:\\n\\n{story_text}"
    },
    "plot-twist": {
        "system_role": "Sen bir olay dönüşü uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi olay dönüşü açısından iyileştir:\\n\\n{story_text}"
    },
    "emotional-authenticity": {
        "system_role": "Sen bir duygusal otantiklik uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi duygusal otantiklik açısından iyileştir:\\n\\n{story_text}"
    },
    "dialogue-naturalness": {
        "system_role": "Sen bir diyalog doğallığı uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi diyalog doğallığı açısından iyileştir:\\n\\n{story_text}"
    },
    "trial-builder": {
        "system_role": "Sen bir deneme inşa uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi deneme inşa açısından iyileştir:\\n\\n{story_text}"
    },
    "contrast-technique": {
        "system_role": "Sen bir kontrast uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi kontrast açısından iyileştir:\\n\\n{story_text}"
    },
    "suspense-adder": {
        "system_role": "Sen bir gerilim uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeye gerilim ekle:\\n\\n{story_text}"
    },
    "memory-optimizer": {
        "system_role": "Sen bir hafıza optimizasyonu uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi hafıza optimizasyonu açısından iyileştir:\\n\\n{story_text}"
    },
    "language-simplifier": {
        "system_role": "Sen bir dil basitleştirme uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi {target_age} yaşındaki çocuklar için basitleştir:\\n\\n{story_text}"
    },
    "progression-builder": {
        "system_role": "Sen bir i̇lerleme inşa uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi i̇lerleme inşa açısından iyileştir:\\n\\n{story_text}"
    },
    "echoing-technique": {
        "system_role": "Sen bir yankılama uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi yankılama açısından iyileştir:\\n\\n{story_text}"
    },
    "description-detail": {
        "system_role": "Sen bir betimleme detayı uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi betimleme detayı açısından iyileştir:\\n\\n{story_text}"
    },
    "interactive-games": {
        "system_role": "Sen bir eğitim uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeden {num_questions} adet çoktan seçmeli soru oluştur:\n\n{story_text}\n\nHer soru için 4 seçenek ver."
    },
    "atmosphere-creator": {
        "system_role": "Sen bir atmosfer yaratma uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi atmosfer yaratma açısından iyileştir:\\n\\n{story_text}"
    },
    "style-adapter": {
        "system_role": "Sen bir stil uyarlama uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi stil uyarlama açısından iyileştir:\\n\\n{story_text}"
    },
    "character-change": {
        "system_role": "Sen bir karakter değişimi uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi karakter değişimi açısından iyileştir:\\n\\n{story_text}"
    },
    "hook-creator": {
        "system_role": "Sen bir kanca yaratma uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeye {hook_type} tipinde ilgi çekici bir başlangıç ekle:\\n\\n{story_text}"
    },
    "chekhov-gun": {
        "system_role": "Sen bir çehov silahı uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi çehov silahı açısından iyileştir:\\n\\n{story_text}"
    },
    "learning-optimizer": {
        "system_role": "Sen bir öğrenme optimizasyonu uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi öğrenme optimizasyonu açısından iyileştir:\\n\\n{story_text}"
    },
    "conflict-adder": {
        "system_role": "Sen bir hikaye çatışma uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeye {conflict_descriptions.get(conflict_type, 'çatışma')} ekle:\n\n{story_text}\n\nÇatışmayı hikayeye doğal bir şekilde entegre et."
    },
    "plot-hole-detector": {
        "system_role": "Sen bir olay örgüsü boşluk tespiti uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi olay örgüsü boşluk tespiti açısından iyileştir:\\n\\n{story_text}"
    },
    "voice-enhancer": {
        "system_role": "Sen bir anlatım sesi uzmanısın.",
        "prompt_template": "Aşağıdaki hikayenin anlatım sesini {voice_style} şekilde geliştir:\\n\\n{story_text}"
    },
    "comfort-provider": {
        "system_role": "Sen bir rahatlatma uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi rahatlatma açısından iyileştir:\\n\\n{story_text}"
    },
    "polish-applier": {
        "system_role": "Sen bir cilalama uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi cilalama açısından iyileştir:\\n\\n{story_text}"
    },
    "description-purposeful": {
        "system_role": "Sen bir betimleme amaçlı uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi betimleme amaçlı açısından iyileştir:\\n\\n{story_text}"
    },
    "emotional-journey": {
        "system_role": "Sen bir duygusal yolculuk uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi duygusal yolculuk açısından iyileştir:\\n\\n{story_text}"
    },
    "catharsis-creator": {
        "system_role": "Sen bir katarsis yaratma uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi katarsis yaratma açısından iyileştir:\\n\\n{story_text}"
    },
    "character-relationship": {
        "system_role": "Sen bir karakter ilişkisi uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi karakter ilişkisi açısından iyileştir:\\n\\n{story_text}"
    },
    "connection-enhancer": {
        "system_role": "Sen bir bağlantı geliştirme uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi bağlantı geliştirme açısından iyileştir:\\n\\n{story_text}"
    },
    "emotional-impact": {
        "system_role": "Sen bir duygusal etki uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi duygusal etki açısından iyileştir:\\n\\n{story_text}"
    },
    "wonder-creator": {
        "system_role": "Sen bir hayret yaratma uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi hayret yaratma açısından iyileştir:\\n\\n{story_text}"
    },
    "ai-editor-advanced": {
        "system_role": "Sen bir hikaye editörüsün.",
        "prompt_template": "Aşağıdaki hikayeyi şu talimata göre düzenle:\n{edit_instruction}\n\nHikaye:\n{story_text}\n\nDüzenlenmiş versiyonu ver."
    },
    "content-converter": {
        "system_role": "Sen bir format dönüştürme uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi {format_instructions.get(target_format, 'farklı formata')} dönüştür:\n\n{story_text}"
    },
    "revelation-creator": {
        "system_role": "Sen bir açığa çıkarma uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi açığa çıkarma açısından iyileştir:\\n\\n{story_text}"
    },
    "content-expansion": {
        "system_role": "Sen bir hikaye genişletme uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi genişlet. \n{expansion_prompts.get(expansion_type, 'Genel olarak genişlet')}:\n\n{story_text}\n\n{f\"Hedef uzunluk: {target_length} kelime\" if target_length else \"\"}"
    },
    "foreshadowing-technique": {
        "system_role": "Sen bir önsezi tekniği uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi önsezi tekniği açısından iyileştir:\\n\\n{story_text}"
    },
    "content-compression": {
        "system_role": "Sen bir içerik sıkıştırma uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi yaklaşık {target_length} kelimeye sıkıştır.\nÖnemli olayları ve karakterleri koru, gereksiz detayları çıkar:\n\n{story_text}"
    },
    "motivation-enhancer": {
        "system_role": "Sen bir motivasyon uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi motivasyon açısından iyileştir:\\n\\n{story_text}"
    },
    "harmony-creator": {
        "system_role": "Sen bir uyum yaratma uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi uyum yaratma açısından iyileştir:\\n\\n{story_text}"
    },
    "plot-resolution": {
        "system_role": "Sen bir olay çözümü uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi olay çözümü açısından iyileştir:\\n\\n{story_text}"
    },
    "ai-rewriter": {
        "system_role": "Sen bir hikaye yazarısın.",
        "prompt_template": "Aşağıdaki hikayeyi {rewrite_style} şekilde yeniden yaz:\\n\\n{story_text}"
    },
    "emotional-connection": {
        "system_role": "Sen bir duygusal bağlantı uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi duygusal bağlantı açısından iyileştir:\\n\\n{story_text}"
    },
    "description-selective": {
        "system_role": "Sen bir betimleme seçici uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi betimleme seçici açısından iyileştir:\\n\\n{story_text}"
    },
    "evolution-tracker": {
        "system_role": "Sen bir evrim takibi uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi evrim takibi açısından iyileştir:\\n\\n{story_text}"
    },
    "callback-creator": {
        "system_role": "Sen bir geri çağırma uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi geri çağırma açısından iyileştir:\\n\\n{story_text}"
    },
    "plot-revelation": {
        "system_role": "Sen bir olay açığa çıkması uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi olay açığa çıkması açısından iyileştir:\\n\\n{story_text}"
    },
    "content-formatting": {
        "system_role": "Sen bir formatlama uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi {format_styles.get(format_style, 'standart')} formatla:\n\n{story_text}"
    },
    "parallel-creator": {
        "system_role": "Sen bir paralel yaratma uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi paralel yaratma açısından iyileştir:\\n\\n{story_text}"
    },
    "progress-tracker": {
        "system_role": "Sen bir i̇lerleme takibi uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi i̇lerleme takibi açısından iyileştir:\\n\\n{story_text}"
    },
    "comprehension-optimizer": {
        "system_role": "Sen bir anlama optimizasyonu uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi anlama optimizasyonu açısından iyileştir:\\n\\n{story_text}"
    },
    "character-dynamic": {
        "system_role": "Sen bir karakter dinamiği uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi karakter dinamiği açısından iyileştir:\\n\\n{story_text}"
    },
    "coherence-creator": {
        "system_role": "Sen bir tutarlılık yaratma uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi tutarlılık yaratma açısından iyileştir:\\n\\n{story_text}"
    },
    "coherence-enhancer": {
        "system_role": "Sen bir tutarlılık geliştirme uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi tutarlılık geliştirme açısından iyileştir:\\n\\n{story_text}"
    },
    "content-filtering": {
        "system_role": "Sen bir içerik moderatörüsün.",
        "prompt_template": "Aşağıdaki hikayeyi {age_group} yaş grubu için {filter_level} seviyede kontrol et.\nUygunsuz içerik, şiddet, korku veya zararlı mesajlar var mı kontrol et:\n\n{story_text}\n\nSadece uygun olup olmadığını ve varsa sorunlu bölümleri belirt."
    },
    "milestone-marker": {
        "system_role": "Sen bir kilometre taşı uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi kilometre taşı açısından iyileştir:\\n\\n{story_text}"
    },
    "interactivity-enhancer": {
        "system_role": "Sen bir etkileşim uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi etkileşim açısından iyileştir:\\n\\n{story_text}"
    },
    "auto-categorization": {
        "system_role": "Sen bir içerik kategorizasyon uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi kategorize et. \nAna kategori, alt kategori, yaş grubu ve temaları belirle:\n\n{story_text}\n\nJSON formatında döndür."
    },
    "parallelism-technique": {
        "system_role": "Sen bir paralellik uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi paralellik açısından iyileştir:\\n\\n{story_text}"
    },
    "symbol-analyzer": {
        "system_role": "Sen bir sembol analizi uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi sembol analizi açısından iyileştir:\\n\\n{story_text}"
    },
    "language-level": {
        "system_role": "Sen bir dil seviyesi uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi dil seviyesi açısından iyileştir:\\n\\n{story_text}"
    },
    "perspective-broadener": {
        "system_role": "Sen bir bakış açısı uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi bakış açısı açısından iyileştir:\\n\\n{story_text}"
    },
    "engagement-builder": {
        "system_role": "Sen bir etkileşim inşa uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi etkileşim inşa açısından iyileştir:\\n\\n{story_text}"
    },
    "preview": {
        "system_role": "Sen bir hikaye editörüsün.",
        "prompt_template": "Aşağıdaki hikayeyi analiz et ve {suggestion_type} için öneriler sun:\n\n{preview[\"preview_text\"]}\n\nÖnerileri liste halinde ver."
    },
    "healing-enhancer": {
        "system_role": "Sen bir i̇yileştirme uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi i̇yileştirme açısından iyileştir:\\n\\n{story_text}"
    },
    "knowledge-embedder": {
        "system_role": "Sen bir bilgi yerleştirme uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi bilgi yerleştirme açısından iyileştir:\\n\\n{story_text}"
    },
    "echo-creator": {
        "system_role": "Sen bir yankı yaratma uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi yankı yaratma açısından iyileştir:\\n\\n{story_text}"
    },
    "artistry-enhancer": {
        "system_role": "Sen bir sanatsallık uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi sanatsallık açısından iyileştir:\\n\\n{story_text}"
    },
    "structure-optimizer": {
        "system_role": "Sen bir yapı optimizasyonu uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi yapı optimizasyonu açısından iyileştir:\\n\\n{story_text}"
    },
    "excitement-adder": {
        "system_role": "Sen bir heyecan yaratma uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeye {level_descriptions.get(excitement_level, 'heyecan')} ekle:\n\n{story_text}\n\nHeyecanı hikayeye doğal bir şekilde entegre et."
    },
    "callback-technique": {
        "system_role": "Sen bir geri çağırma uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi geri çağırma açısından iyileştir:\\n\\n{story_text}"
    },
    "brilliance-achiever": {
        "system_role": "Sen bir parlaklık uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi parlaklık açısından iyileştir:\\n\\n{story_text}"
    },
    "playfulness-adder": {
        "system_role": "Sen bir oyunculuk uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi oyunculuk açısından iyileştir:\\n\\n{story_text}"
    },
    "world-geography": {
        "system_role": "Sen bir dünya coğrafyası uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi dünya coğrafyası açısından iyileştir:\\n\\n{story_text}"
    },
    "paradox-creator": {
        "system_role": "Sen bir paradoks yaratma uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi paradoks yaratma açısından iyileştir:\\n\\n{story_text}"
    },
    "participation-creator": {
        "system_role": "Sen bir katılım uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi katılım açısından iyileştir:\\n\\n{story_text}"
    },
    "irony-adder": {
        "system_role": "Sen bir i̇roni ekleme uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi i̇roni ekleme açısından iyileştir:\\n\\n{story_text}"
    },
    "medium-adapter": {
        "system_role": "Sen bir medya uyarlama uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi medya uyarlama açısından iyileştir:\\n\\n{story_text}"
    },
    "description-vividness": {
        "system_role": "Sen bir betimleme canlılığı uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi betimleme canlılığı açısından iyileştir:\\n\\n{story_text}"
    },
    "beginning-changer": {
        "system_role": "Sen bir hikaye başlangıcı uzmanısın.",
        "prompt_template": "Aşağıdaki hikayenin başlangıcını {style_descriptions.get(beginning_style, 'farklı bir stille')} değiştir:\n\n{story_text}"
    },
    "museum": {
        "system_role": "Sen bir müze küratörüsün.",
        "prompt_template": "Aşağıdaki hikayedeki önemli nesneleri, eşyaları ve eserleri bul.\nHer biri için kısa bir açıklama yap:\n\n{story_text}"
    },
    "impact-optimizer": {
        "system_role": "Sen bir etki optimizasyonu uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi etki optimizasyonu açısından iyileştir:\\n\\n{story_text}"
    },
    "resolution-adder": {
        "system_role": "Sen bir hikaye çözüm uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeye {resolution_descriptions.get(resolution_type, 'çözüm')} ekle:\n\n{story_text}\n\nÇözümü hikayenin çatışmalarını çözecek şekilde yaz."
    },
    "principle-teacher": {
        "system_role": "Sen bir i̇lke öğretme uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi i̇lke öğretme açısından iyileştir:\\n\\n{story_text}"
    },
    "character-depth": {
        "system_role": "Sen bir karakter derinliği uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi karakter derinliği açısından iyileştir:\\n\\n{story_text}"
    },
    "hope-enhancer": {
        "system_role": "Sen bir umut uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi umut açısından iyileştir:\\n\\n{story_text}"
    },
    "plot-complication": {
        "system_role": "Sen bir olay karmaşası uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi olay karmaşası açısından iyileştir:\\n\\n{story_text}"
    },
    "complexity-adapter": {
        "system_role": "Sen bir karmaşıklık uyarlama uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi karmaşıklık uyarlama açısından iyileştir:\\n\\n{story_text}"
    },
    "dialogue-variety": {
        "system_role": "Sen bir diyalog çeşitliliği uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi diyalog çeşitliliği açısından iyileştir:\\n\\n{story_text}"
    },
    "character-motivation": {
        "system_role": "Sen bir karakter motivasyonu uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi karakter motivasyonu açısından iyileştir:\\n\\n{story_text}"
    },
    "emotion-enhancer": {
        "system_role": "Sen bir duygu uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeye duygusal derinlik ekle:\\n\\n{story_text}"
    },
    "auto-summary": {
        "system_role": "Sen bir özet uzmanısın.",
        "prompt_template": "Aşağıdaki hikayenin {length_instructions.get(summary_length, 'orta uzunlukta')} özetini oluştur:\n\n{story_text}"
    },
    "subplot-creator": {
        "system_role": "Sen bir alt olay yaratma uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi alt olay yaratma açısından iyileştir:\\n\\n{story_text}"
    },
    "description-atmospheric": {
        "system_role": "Sen bir betimleme atmosferik uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi betimleme atmosferik açısından iyileştir:\\n\\n{story_text}"
    },
    "world-rules": {
        "system_role": "Sen bir dünya kuralları uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi dünya kuralları açısından iyileştir:\\n\\n{story_text}"
    },
    "improvement-shower": {
        "system_role": "Sen bir i̇yileşme gösterme uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi i̇yileşme gösterme açısından iyileştir:\\n\\n{story_text}"
    },
    "transition-enhancer": {
        "system_role": "Sen bir geçiş uzmanısın.",
        "prompt_template": "Aşağıdaki hikayedeki geçişleri iyileştir:\\n\\n{story_text}"
    },
    "content-enrichment": {
        "system_role": "Sen bir hikaye zenginleştirme uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi zenginleştir. \n{enrichment_prompts.get(enrichment_type, 'Genel olarak zenginleştir')}:\n\n{story_text}"
    },
    "description-enhancer": {
        "system_role": "Sen bir betimleme uzmanısın.",
        "prompt_template": "Aşağıdaki hikayenin betimlemelerini zenginleştir:\\n\\n{story_text}"
    },
    "dialogue-subtext": {
        "system_role": "Sen bir diyalog alt metni uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi diyalog alt metni açısından iyileştir:\\n\\n{story_text}"
    },
    "content-splitter": {
        "system_role": "Sen bir hikaye bölme uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi {num_chapters} bölüme ayır.\nHer bölüm bağımsız ama birbirine bağlı olsun:\n\n{story_text}\n\nHer bölüm için başlık ve içerik ver."
    },
    "improvement": {
        "system_role": "Sen bir edebiyat editörüsün. Hikâyeleri analiz edip iyileştirme önerileri sunuyorsun.",
        "prompt_template": "\nAşağıdaki hikâyeyi analiz et ve iyileştirme önerileri sun. JSON formatında döndür.\n\nHikâye:\n{story_text}\n\nAnaliz etmen gerekenler:\n1. Yazım ve dil bilgisi hataları\n2. Cümle yapısı ve akıcılık\n3. Kelime seçimi ve çeşitlilik\n4. Hikâye yapısı (giriş, gelişme, sonuç)\n5. Karakter gelişimi\n6. Diyalog kalitesi\n7. Betimleme kalitesi\n8. Genel okunabilirlik\n\nHer kategori için:\n- Skor (0-100)\n- Güçlü yönler\n- İyileştirme önerileri\n- Örnek cümleler (iyileştirilmiş versiyonlar)\n\nJSON formatında döndür:\n{{\n  \"overall_score\": 75,\n  \"categories\": {{\n    \"spelling_grammar\": {{\n      \"score\": 80,\n      \"strengths\": [\"Güçlü yönler\"],\n      \"suggestions\": [\"İyileştirme önerileri\"],\n      \"examples\": [{{\"original\": \"Cümle\", \"improved\": \"İyileştirilmiş cümle\"}}]\n    }},\n    \"sentence_structure\": {{...}},\n    \"word_choice\": {{...}},\n    \"story_structure\": {{...}},\n    \"character_development\": {{...}},\n    \"dialogue\": {{...}},\n    \"description\": {{...}},\n    \"readability\": {{...}}\n  }},\n  \"top_suggestions\": [\n    \"En önemli 3-5 öneri\"\n  ],\n  \"readability_score\": 65\n}}\n"
    },
    "beauty-creator": {
        "system_role": "Sen bir güzellik yaratma uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi güzellik yaratma açısından iyileştir:\\n\\n{story_text}"
    },
    "engagement-optimizer": {
        "system_role": "Sen bir etkileşim optimizasyonu uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi etkileşim optimizasyonu açısından iyileştir:\\n\\n{story_text}"
    },
    "emotional-layers": {
        "system_role": "Sen bir duygusal katmanlar uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi duygusal katmanlar açısından iyileştir:\\n\\n{story_text}"
    },
    "character-growth": {
        "system_role": "Sen bir karakter gelişimi uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi karakter gelişimi açısından iyileştir:\\n\\n{story_text}"
    },
    "romance-adder": {
        "system_role": "Sen bir romantizm uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeye {level_descriptions.get(romance_level, 'romantizm')} ekle.\nÇocuklar için uygun ve masum bir şekilde:\n\n{story_text}"
    },
    "time-changer": {
        "system_role": "Sen bir zaman değiştirme uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi {time_descriptions.get(new_time_period, 'farklı bir zaman periyoduna')} taşı:\n\n{story_text}"
    },
    "style-changer": {
        "system_role": "Sen bir stil değiştirme uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi {style_descriptions.get(new_style, 'farklı bir stile')} dönüştür:\n\n{story_text}"
    },
    "action-enhancer": {
        "system_role": "Sen bir aksiyon uzmanısın.",
        "prompt_template": "Aşağıdaki hikayenin aksiyon sahnelerini güçlendir:\\n\\n{story_text}"
    },
    "quality-ensurer": {
        "system_role": "Sen bir kalite güvencesi uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi kalite güvencesi açısından iyileştir:\\n\\n{story_text}"
    },
    "description-flowing": {
        "system_role": "Sen bir betimleme akıcı uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi betimleme akıcı açısından iyileştir:\\n\\n{story_text}"
    },
    "emotional-range": {
        "system_role": "Sen bir duygusal aralık uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi duygusal aralık açısından iyileştir:\\n\\n{story_text}"
    },
    "emotional-arc": {
        "system_role": "Sen bir duygusal yay uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi duygusal yay açısından iyileştir:\\n\\n{story_text}"
    },
    "amazement-enhancer": {
        "system_role": "Sen bir hayranlık uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi hayranlık açısından iyileştir:\\n\\n{story_text}"
    },
    "tone-adjuster": {
        "system_role": "Sen bir ton ayarlama uzmanısın.",
        "prompt_template": "Aşağıdaki hikayenin tonunu {tone_descriptions.get(target_tone, 'farklı bir tona')} ayarla:\n\n{story_text}"
    },
    "world-culture": {
        "system_role": "Sen bir dünya kültürü uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi dünya kültürü açısından iyileştir:\\n\\n{story_text}"
    },
    "plot-thread": {
        "system_role": "Sen bir olay ipliği uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi olay ipliği açısından iyileştir:\\n\\n{story_text}"
    },
    "description-balanced": {
        "system_role": "Sen bir betimleme dengeli uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi betimleme dengeli açısından iyileştir:\\n\\n{story_text}"
    },
    "culture-adaptation": {
        "system_role": "Sen bir kültür uyarlama uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi kültür uyarlama açısından iyileştir:\\n\\n{story_text}"
    },
    "dialogue-voice": {
        "system_role": "Sen bir diyalog sesi uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi diyalog sesi açısından iyileştir:\\n\\n{story_text}"
    },
    "vocabulary-enhancer": {
        "system_role": "Sen bir kelime hazinesi uzmanısın.",
        "prompt_template": "Aşağıdaki hikayenin kelime hazinesini {enhancement_level} seviyede geliştir:\\n\\n{story_text}"
    },
    "emotional-depth": {
        "system_role": "Sen bir duygusal derinlik uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi duygusal derinlik açısından iyileştir:\\n\\n{story_text}"
    },
    "character-replacer": {
        "system_role": "Sen bir karakter değiştirme uzmanısın.",
        "prompt_template": "Aşağıdaki hikayede '{old_character}' karakterini '{new_character}' ile değiştir.\nKarakterin özelliklerini ve rollerini yeni karaktere uyarla:\n\n{story_text}"
    },
    "theme-strength": {
        "system_role": "Sen bir tema gücü uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi tema gücü açısından iyileştir:\\n\\n{story_text}"
    },
    "moral-adder": {
        "system_role": "Sen bir ahlaki ders uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeye ahlaki bir ders ekle.\n{f\"Tema: {moral_theme}\" if moral_theme else \"Hikayeden uygun bir ders çıkar\"}:\n\n{story_text}\n\nDersi hikayeye doğal bir şekilde entegre et."
    },
    "learning-curve": {
        "system_role": "Sen bir öğrenme eğrisi uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi öğrenme eğrisi açısından iyileştir:\\n\\n{story_text}"
    },
    "engagement-analyzer": {
        "system_role": "Sen bir etkileşim analizi uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi etkileşim analizi açısından iyileştir:\\n\\n{story_text}"
    },
    "dialogue-purpose": {
        "system_role": "Sen bir diyalog amacı uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi diyalog amacı açısından iyileştir:\\n\\n{story_text}"
    },
    "world-politics": {
        "system_role": "Sen bir dünya politikası uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi dünya politikası açısından iyileştir:\\n\\n{story_text}"
    },
    "pace-variation": {
        "system_role": "Sen bir tempo çeşitliliği uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi tempo çeşitliliği açısından iyileştir:\\n\\n{story_text}"
    },
    "emotion-analysis": {
        "system_role": "Sen bir duygu analiz uzmanısın.",
        "prompt_template": "Aşağıdaki hikayedeki duyguları analiz et. Her bölüm için:\n1. Baskın duygu (mutluluk, üzüntü, korku, heyecan, vb.)\n2. Duygu yoğunluğu (1-10 arası)\n3. Duygu geçişleri\n\nHikaye:\n{story_text}\n\nJSON formatında döndür."
    },
    "theme-enhancer": {
        "system_role": "Sen bir tema uzmanısın.",
        "prompt_template": "Aşağıdaki hikayenin temasını güçlendir{f': {theme}' if theme else ''}:\\n\\n{story_text}"
    },
    "content-merger": {
        "system_role": "Sen bir hikaye birleştirme uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeleri {style_instructions.get(merge_style, 'birleştir')}:\n\n{stories_text}\n\nTutarlı ve akıcı bir hikaye oluştur."
    },
    "balance-optimizer": {
        "system_role": "Sen bir denge optimizasyonu uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi denge optimizasyonu açısından iyileştir:\\n\\n{story_text}"
    },
    "comment-analysis": {
        "system_role": "Sen bir yorum analiz uzmanısın.",
        "prompt_template": "Aşağıdaki yorumları analiz et:\n{comments_text}\n\nŞunları belirle:\n1. Genel duygu durumu (pozitif/negatif/nötr)\n2. Ana temalar ve konular\n3. Öneriler ve geri bildirimler\n4. En çok bahsedilen özellikler"
    },
    "voice-commands": {
        "system_role": "Sen bir hikaye yazarısın.",
        "prompt_template": "Kullanıcı şunu söyledi: {audio_text}\nBu komuttan bir hikaye oluştur. Kısa ve çocuklar için uygun olsun."
    },
    "show-dont-tell": {
        "system_role": "Sen bir göster anlatma uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi göster anlatma açısından iyileştir:\\n\\n{story_text}"
    },
    "red-herring": {
        "system_role": "Sen bir kırmızı ringa uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi kırmızı ringa açısından iyileştir:\\n\\n{story_text}"
    },
    "timeline-analyzer": {
        "system_role": "Sen bir zaman çizelgesi analizi uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi zaman çizelgesi analizi açısından iyileştir:\\n\\n{story_text}"
    },
    "mirroring-technique": {
        "system_role": "Sen bir yansıtma uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi yansıtma açısından iyileştir:\\n\\n{story_text}"
    },
    "plot-point": {
        "system_role": "Sen bir olay noktası uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi olay noktası açısından iyileştir:\\n\\n{story_text}"
    },
    "analysis": {
        "system_role": "Sen bir edebiyat analiz uzmanısın. Hikâyeleri detaylı analiz ediyorsun.",
        "prompt_template": "\nAşağıdaki hikâyeyi detaylı analiz et ve JSON formatında sonuçları döndür.\n\nHikâye:\n{story_text}\n\nAnaliz etmen gerekenler:\n1. Duygu analizi: Hikâyedeki ana duygular (mutlu, üzgün, korkulu, heyecanlı, vb.)\n2. Karakter analizi: Ana karakterler, rolleri, özellikleri\n3. Okuma seviyesi: Yaş grubu, zorluk seviyesi (kolay, orta, zor)\n4. Tema analizi: Ana temalar, mesajlar\n5. Kelime sayısı, cümle sayısı\n6. Okuma süresi tahmini (dakika)\n7. Önerilen yaş grubu\n\nJSON formatında döndür:\n{{\n  \"emotions\": {{\n    \"primary\": \"ana_duygu\",\n    \"secondary\": [\"ikincil_duygu1\", \"ikincil_duygu2\"],\n    \"emotion_score\": {{\n      \"happy\": 0.7,\n      \"sad\": 0.2,\n      \"excited\": 0.8,\n      \"scared\": 0.1\n    }}\n  }},\n  \"characters\": [\n    {{\n      \"name\": \"Karakter adı\",\n      \"role\": \"Ana karakter / Yan karakter\",\n      \"personality\": \"Kişilik özellikleri\",\n      \"importance\": \"yüksek / orta / düşük\"\n    }}\n  ],\n  \"reading_level\": {{\n    \"difficulty\": \"kolay / orta / zor\",\n    \"age_group\": \"5-7 / 8-10 / 11-13 / 14+\",\n    \"grade_level\": \"1-2 / 3-4 / 5-6 / 7+\"\n  }},\n  \"themes\": [\"tema1\", \"tema2\", \"tema3\"],\n  \"statistics\": {{\n    \"word_count\": 500,\n    \"sentence_count\": 30,\n    \"paragraph_count\": 5,\n    \"average_words_per_sentence\": 16.7,\n    \"reading_time_minutes\": 3\n  }},\n  \"recommended_age\": \"5-8\",\n  \"keywords\": [\"anahtar_kelime1\", \"anahtar_kelime2\"]\n}}\n"
    },
    "emotional-balance": {
        "system_role": "Sen bir duygusal denge uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi duygusal denge açısından iyileştir:\\n\\n{story_text}"
    },
    "dialogue-pace": {
        "system_role": "Sen bir diyalog temposu uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi diyalog temposu açısından iyileştir:\\n\\n{story_text}"
    },
    "transformation-shower": {
        "system_role": "Sen bir dönüşüm gösterme uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi dönüşüm gösterme açısından iyileştir:\\n\\n{story_text}"
    },
    "identification-enhancer": {
        "system_role": "Sen bir özdeşleşme uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi özdeşleşme açısından iyileştir:\\n\\n{story_text}"
    },
    "chapter-structure": {
        "system_role": "Sen bir bölüm yapısı uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi bölüm yapısı açısından iyileştir:\\n\\n{story_text}"
    },
    "description-sensory": {
        "system_role": "Sen bir betimleme duyusal uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi betimleme duyusal açısından iyileştir:\\n\\n{story_text}"
    },
    "world-detail": {
        "system_role": "Sen bir dünya detayları uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi dünya detayları açısından iyileştir:\\n\\n{story_text}"
    },
    "flow-optimizer": {
        "system_role": "Sen bir akış optimizasyonu uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi akış optimizasyonu açısından iyileştir:\\n\\n{story_text}"
    },
    "rhythm-enhancer": {
        "system_role": "Sen bir ritim uzmanısın.",
        "prompt_template": "Aşağıdaki hikayenin ritmini geliştir, cümle uzunluklarını çeşitlendir:\\n\\n{story_text}"
    },
    "foreshadowing-adder": {
        "system_role": "Sen bir önsezi uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeye önsezi (foreshadowing) ekle:\\n\\n{story_text}"
    },
    "world-history": {
        "system_role": "Sen bir dünya tarihi uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi dünya tarihi açısından iyileştir:\\n\\n{story_text}"
    },
    "juxtaposition": {
        "system_role": "Sen bir yan yana koyma uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi yan yana koyma açısından iyileştir:\\n\\n{story_text}"
    },
    "world-magic": {
        "system_role": "Sen bir dünya büyüsü uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi dünya büyüsü açısından iyileştir:\\n\\n{story_text}"
    },
    "emotional-resonance": {
        "system_role": "Sen bir duygusal rezonans uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi duygusal rezonans açısından iyileştir:\\n\\n{story_text}"
    },
    "plot-complexity": {
        "system_role": "Sen bir olay örgüsü karmaşıklığı uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi olay örgüsü karmaşıklığı açısından iyileştir:\\n\\n{story_text}"
    },
    "variety-creator": {
        "system_role": "Sen bir çeşitlilik yaratma uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi çeşitlilik yaratma açısından iyileştir:\\n\\n{story_text}"
    },
    "world-religion": {
        "system_role": "Sen bir dünya dini uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi dünya dini açısından iyileştir:\\n\\n{story_text}"
    },
    "theater": {
        "system_role": "Sen bir tiyatro senaryo yazarısın.",
        "prompt_template": "Aşağıdaki hikayeyi {num_actors} kişilik bir tiyatro oyununa dönüştür. \nDiyaloglar, sahne talimatları ve karakter tanımlamaları ekle:\n\n{story_text}\n\nTiyatro formatında döndür."
    },
    "dialogue-realism": {
        "system_role": "Sen bir diyalog gerçekçiliği uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi diyalog gerçekçiliği açısından iyileştir:\\n\\n{story_text}"
    },
    "plagiarism-checker": {
        "system_role": "Sen bir intihal kontrol uzmanısın.",
        "prompt_template": "Aşağıdaki metinde intihal var mı kontrol et:\\n\\n{story_text}"
    },
    "pacing-optimizer": {
        "system_role": "Sen bir tempo uzmanısın.",
        "prompt_template": "Aşağıdaki hikayenin temposunu {pacing_type} şekilde optimize et:\\n\\n{story_text}"
    },
    "final-touch": {
        "system_role": "Sen bir son dokunuş uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi son dokunuş açısından iyileştir:\\n\\n{story_text}"
    },
    "world-economy": {
        "system_role": "Sen bir dünya ekonomisi uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi dünya ekonomisi açısından iyileştir:\\n\\n{story_text}"
    },
    "readability-analyzer": {
        "system_role": "Sen bir okunabilirlik analizi uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi okunabilirlik analizi açısından iyileştir:\\n\\n{story_text}"
    },
    "goal-setter": {
        "system_role": "Sen bir hedef belirleme uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi hedef belirleme açısından iyileştir:\\n\\n{story_text}"
    },
    "complexity-analyzer": {
        "system_role": "Sen bir karmaşıklık analizi uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi karmaşıklık analizi açısından iyileştir:\\n\\n{story_text}"
    },
    "auto-title": {
        "system_role": "Sen bir başlık yazım uzmanısın.",
        "prompt_template": "Aşağıdaki hikaye için {num_titles} adet {style_instructions.get(title_style, 'yaratıcı')} başlık öner:\n\n{story_text}\n\nHer başlık farklı bir açıdan yaklaşsın."
    },
    "choose-your-adventure": {
        "system_role": "Sen bir interaktif hikaye uzmanısın.",
        "prompt_template": "Aşağıdaki hikaye bölümü için {num_choices} farklı seçenek oluştur.\nHer seçenek farklı bir sonuca götürmeli:\n\n{story_text}\n\nSeçenekleri ve her seçeneğin kısa açıklamasını ver."
    },
    "outline": {
        "system_role": "Sen bir hikâye planlamacısısın. Hikâyeler için özet ve plan oluşturursun.",
        "prompt_template": "Aşağıdaki temaya göre bir {story_type} hikâyesi için kısa bir özet oluştur:\n\nTema: {theme}\n\nÖzet 2-3 paragraf uzunluğunda olsun ve hikâyenin ana hatlarını, karakterleri ve olay örgüsünü içersin."
    },
    "three-act-structure": {
        "system_role": "Sen bir üç perde yapı uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi üç perde yapı açısından iyileştir:\\n\\n{story_text}"
    },
    "climax-enhancer": {
        "system_role": "Sen bir doruk noktası uzmanısın.",
        "prompt_template": "Aşağıdaki hikayenin doruk noktasını güçlendir:\\n\\n{story_text}"
    },
    "audience-adapter": {
        "system_role": "Sen bir kitle uyarlama uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi kitle uyarlama açısından iyileştir:\\n\\n{story_text}"
    },
    "parallel-plot": {
        "system_role": "Sen bir paralel olay uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi paralel olay açısından iyileştir:\\n\\n{story_text}"
    },
    "character-map": {
        "system_role": "Sen bir hikaye analiz uzmanısın.",
        "prompt_template": "Aşağıdaki hikayedeki karakterleri bul ve analiz et. Her karakter için:\n1. İsim\n2. Rol (ana karakter, yan karakter, kötü karakter, vb.)\n3. Özellikler\n4. Diğer karakterlerle ilişkileri\n\nHikaye:\n{story_text}\n\nJSON formatında döndür."
    },
    "value-embedder": {
        "system_role": "Sen bir değer yerleştirme uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi değer yerleştirme açısından iyileştir:\\n\\n{story_text}"
    },
    "surprise-adder": {
        "system_role": "Sen bir sürpriz ekleme uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi sürpriz ekleme açısından iyileştir:\\n\\n{story_text}"
    },
    "joy-enhancer": {
        "system_role": "Sen bir neşe uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi neşe açısından iyileştir:\\n\\n{story_text}"
    },
    "age-adaptation": {
        "system_role": "Sen bir yaş uyarlama uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi yaş uyarlama açısından iyileştir:\\n\\n{story_text}"
    },
    "skill-builder": {
        "system_role": "Sen bir beceri inşa uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi beceri inşa açısından iyileştir:\\n\\n{story_text}"
    },
    "understanding-builder": {
        "system_role": "Sen bir anlayış inşa uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi anlayış inşa açısından iyileştir:\\n\\n{story_text}"
    },
    "metaphor-analyzer": {
        "system_role": "Sen bir metafor analizi uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi metafor analizi açısından iyileştir:\\n\\n{story_text}"
    },
    "world-society": {
        "system_role": "Sen bir dünya toplumu uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi dünya toplumu açısından iyileştir:\\n\\n{story_text}"
    },
    "content-analysis": {
        "system_role": "Sen bir hikaye analiz uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi kapsamlı bir şekilde analiz et:\n1. Yapı ve kurgu\n2. Karakterler\n3. Temalar\n4. Dil ve anlatım\n5. Güçlü ve zayıf yönler\n\nHikaye:\n{story_text}"
    },
    "content-suggestions": {
        "system_role": "Sen bir hikaye yazım asistanısın.",
        "prompt_template": "Aşağıdaki hikayeye devam etmek için 3 farklı öneri sun:\n\n{current_text}\n\nHer öneri farklı bir yöne gitsin."
    },
    "length-adapter": {
        "system_role": "Sen bir uzunluk uyarlama uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi uzunluk uyarlama açısından iyileştir:\\n\\n{story_text}"
    },
    "perfection-seeker": {
        "system_role": "Sen bir mükemmellik arayışı uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi mükemmellik arayışı açısından iyileştir:\\n\\n{story_text}"
    },
    "empathy-builder": {
        "system_role": "Sen bir empati inşa uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi empati inşa açısından iyileştir:\\n\\n{story_text}"
    },
    "inline-search": {
        "system_role": "Sen bir metin analiz uzmanısın.",
        "prompt_template": "Aşağıdaki hikayede \"{query}\" ile ilgili bölümleri bul ve listele:\n\n{full_text}\n\nSadece ilgili bölümleri ve pozisyonlarını ver."
    },
    "character-quirk": {
        "system_role": "Sen bir karakter tuhaflığı uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi karakter tuhaflığı açısından iyileştir:\\n\\n{story_text}"
    },
    "entertainment-adder": {
        "system_role": "Sen bir eğlence uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeye {entertainment_descriptions.get(entertainment_type, 'eğlence')} ekle:\n\n{story_text}\n\nEğlenceyi hikayeye doğal bir şekilde entegre et."
    },
    "description-engaging": {
        "system_role": "Sen bir betimleme etkileyici uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi betimleme etkileyici açısından iyileştir:\\n\\n{story_text}"
    },
    "inspiration-enhancer": {
        "system_role": "Sen bir i̇lham uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi i̇lham açısından iyileştir:\\n\\n{story_text}"
    },
    "mirror-creator": {
        "system_role": "Sen bir ayna yaratma uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi ayna yaratma açısından iyileştir:\\n\\n{story_text}"
    },
    "twist-creator": {
        "system_role": "Sen bir dönüş yaratma uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi dönüş yaratma açısından iyileştir:\\n\\n{story_text}"
    },
    "consistency-checker": {
        "system_role": "Sen bir tutarlılık kontrolü uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi tutarlılık kontrolü açısından iyileştir:\\n\\n{story_text}"
    },
    "clarity-optimizer": {
        "system_role": "Sen bir netlik optimizasyonu uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi netlik optimizasyonu açısından iyileştir:\\n\\n{story_text}"
    },
    "mission-creator": {
        "system_role": "Sen bir misyon yaratma uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi misyon yaratma açısından iyileştir:\\n\\n{story_text}"
    },
    "character-arc": {
        "system_role": "Sen bir karakter yayı uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi karakter yayı açısından iyileştir:\\n\\n{story_text}"
    },
    "interest-maintainer": {
        "system_role": "Sen bir i̇lgi sürdürme uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi i̇lgi sürdürme açısından iyileştir:\\n\\n{story_text}"
    },
    "achievement-celebrator": {
        "system_role": "Sen bir başarı kutlama uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi başarı kutlama açısından iyileştir:\\n\\n{story_text}"
    },
    "unity-creator": {
        "system_role": "Sen bir birlik yaratma uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi birlik yaratma açısından iyileştir:\\n\\n{story_text}"
    },
    "obstacle-creator": {
        "system_role": "Sen bir engel yaratma uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi engel yaratma açısından iyileştir:\\n\\n{story_text}"
    },
    "hero-journey": {
        "system_role": "Sen bir kahraman yolculuğu uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi kahraman yolculuğu açısından iyileştir:\\n\\n{story_text}"
    },
    "development-tracker": {
        "system_role": "Sen bir gelişim takibi uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi gelişim takibi açısından iyileştir:\\n\\n{story_text}"
    },
    "plot-balancer": {
        "system_role": "Sen bir olay dengeleyici uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi olay dengeleyici açısından iyileştir:\\n\\n{story_text}"
    },
    "wisdom-sharer": {
        "system_role": "Sen bir bilgelik paylaşma uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi bilgelik paylaşma açısından iyileştir:\\n\\n{story_text}"
    },
    "critical-thinking": {
        "system_role": "Sen bir eleştirel düşünme uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi eleştirel düşünme açısından iyileştir:\\n\\n{story_text}"
    },
    "music-integration": {
        "system_role": "Sen bir şarkı sözü yazarısın.",
        "prompt_template": "Aşağıdaki hikayeden çocuklar için bir şarkı sözü oluştur. \nMelodik, eğlenceli ve akılda kalıcı olsun:\n\n{story_text}\n\nŞarkı sözlerini verse-chorus formatında ver."
    },
    "alliteration-enhancer": {
        "system_role": "Sen bir aliterasyon uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeye aliterasyon ekle:\\n\\n{story_text}"
    },
    "word-choice-optimizer": {
        "system_role": "Sen bir kelime seçimi uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi kelime seçimi açısından iyileştir:\\n\\n{story_text}"
    },
    "pace-creator": {
        "system_role": "Sen bir tempo yaratma uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi tempo yaratma açısından iyileştir:\\n\\n{story_text}"
    },
    "timeline-visualization": {
        "system_role": "Sen bir hikaye analiz uzmanısın.",
        "prompt_template": "Aşağıdaki hikayedeki olayları kronolojik sıraya göre listele. Her olay için:\n1. Zaman/konum\n2. Olay açıklaması\n3. İlgili karakterler\n\nHikaye:\n{story_text}\n\nJSON formatında döndür."
    },
    "insights": {
        "system_role": "Sen bir hikâye analiz uzmanısın. Derinlemesine içgörüler sunuyorsun.",
        "prompt_template": "\nAşağıdaki hikâye analizini kullanarak derinlemesine içgörüler oluştur.\n\nHikâye Analizi:\n{json.dumps(analysis, ensure_ascii=False, indent=2)}\n\nJSON formatında döndür:\n{{\n  \"key_insights\": [\n    \"İçgörü 1\",\n    \"İçgörü 2\",\n    \"İçgörü 3\"\n  ],\n  \"strengths\": [\"Güçlü yön 1\", \"Güçlü yön 2\"],\n  \"weaknesses\": [\"Zayıf yön 1\", \"Zayıf yön 2\"],\n  \"recommendations\": [\"Öneri 1\", \"Öneri 2\"],\n  \"target_audience\": \"Hedef kitle\",\n  \"unique_selling_points\": [\"Özellik 1\", \"Özellik 2\"]\n}}\n"
    },
    "confidence-builder": {
        "system_role": "Sen bir güven inşa uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi güven inşa açısından iyileştir:\\n\\n{story_text}"
    },
    "framing-technique": {
        "system_role": "Sen bir çerçeveleme uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi çerçeveleme açısından iyileştir:\\n\\n{story_text}"
    },
    "imagery-enhancer": {
        "system_role": "Sen bir görsel betimleme uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeye görsel betimlemeler ekle:\\n\\n{story_text}"
    },
    "masterpiece-creator": {
        "system_role": "Sen bir başyapıt yaratma uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi başyapıt yaratma açısından iyileştir:\\n\\n{story_text}"
    },
    "format-converter": {
        "system_role": "Sen bir format dönüştürme uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi format dönüştürme açısından iyileştir:\\n\\n{story_text}"
    },
    "character-flaw": {
        "system_role": "Sen bir karakter kusuru uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi karakter kusuru açısından iyileştir:\\n\\n{story_text}"
    },
    "symbolism-adder": {
        "system_role": "Sen bir sembolizm uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeye sembolizm ekle:\\n\\n{story_text}"
    },
    "connection-builder": {
        "system_role": "Sen bir bağlantı inşa uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi bağlantı inşa açısından iyileştir:\\n\\n{story_text}"
    },
    "writing-assistant": {
        "system_role": "Sen bir metin editörüsün.",
        "prompt_template": "Aşağıdaki hikayeye devam etmek için öneriler sun.\nMevcut metin:\n{current_text}\n\n{f\"Bağlam: {context}\" if context else \"\"}\n\n{len(current_text.split())} kelimelik bir devam önerisi yap."
    },
    "tone-consistency": {
        "system_role": "Sen bir ton tutarlılığı uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi ton tutarlılığı açısından iyileştir:\\n\\n{story_text}"
    },
    "character-consistency": {
        "system_role": "Sen bir karakter tutarlılığı uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi karakter tutarlılığı açısından iyileştir:\\n\\n{story_text}"
    },
    "curiosity-sparker": {
        "system_role": "Sen bir merak uyandırma uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi merak uyandırma açısından iyileştir:\\n\\n{story_text}"
    },
    "smart-tagging": {
        "system_role": "Sen bir içerik etiketleme uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi analiz et ve uygun etiketler öner.\n5-10 arası etiket ver:\n\n{story_text}"
    },
    "plot-weaver": {
        "system_role": "Sen bir olay dokuyucu uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi olay dokuyucu açısından iyileştir:\\n\\n{story_text}"
    },
    "character-backstory": {
        "system_role": "Sen bir karakter geçmişi uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi karakter geçmişi açısından iyileştir:\\n\\n{story_text}"
    },
    "perspective-changer": {
        "system_role": "Sen bir perspektif değiştirme uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi {perspective_descriptions.get(new_perspective, 'farklı bir perspektife')} dönüştür:\n\n{story_text}"
    },
    "mystery-adder": {
        "system_role": "Sen bir gizem yaratma uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeye {mystery_descriptions.get(mystery_type, 'gizem')} ekle:\n\n{story_text}\n\nGizemi hikayeye doğal bir şekilde entegre et."
    },
    "paragraph-structure": {
        "system_role": "Sen bir paragraf yapısı uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi paragraf yapısı açısından iyileştir:\\n\\n{story_text}"
    },
    "world-building": {
        "system_role": "Sen bir dünya yapımı uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeden detaylı bir dünya oluştur. Şunları ekle:\n1. Coğrafya ve yerler\n2. Kültür ve toplum\n3. Tarih ve mitoloji\n4. Teknoloji veya sihir sistemi\n5. Önemli karakterler ve gruplar\n\nHikaye:\n{story_text}\n\nDünya türü: {world_type}"
    },
    "rhythm-creator": {
        "system_role": "Sen bir ritim yaratma uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi ritim yaratma açısından iyileştir:\\n\\n{story_text}"
    },
    "contrast-enhancer": {
        "system_role": "Sen bir kontrast geliştirme uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi kontrast geliştirme açısından iyileştir:\\n\\n{story_text}"
    },
    "quality-scorer": {
        "system_role": "Sen bir hikaye değerlendirme uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi 1-10 arası puanla:\\n\\n{story_text}"
    },
    "awareness-enhancer": {
        "system_role": "Sen bir farkındalık uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi farkındalık açısından iyileştir:\\n\\n{story_text}"
    },
    "challenge-builder": {
        "system_role": "Sen bir meydan okuma uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi meydan okuma açısından iyileştir:\\n\\n{story_text}"
    },
    "middle-changer": {
        "system_role": "Sen bir hikaye orta kısmı uzmanısın.",
        "prompt_template": "Aşağıdaki hikayenin ortasına {enhancement_descriptions.get(middle_enhancement, 'geliştirme')} ekle:\n\n{story_text}"
    },
    "quest-builder": {
        "system_role": "Sen bir görev inşa uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi görev inşa açısından iyileştir:\\n\\n{story_text}"
    },
    "tension-builder": {
        "system_role": "Sen bir gerginlik uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeye gerginlik ekle:\\n\\n{story_text}"
    },
    "arc-builder": {
        "system_role": "Sen bir yay inşa uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi yay inşa açısından iyileştir:\\n\\n{story_text}"
    },
    "laughter-creator": {
        "system_role": "Sen bir kahkaha uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi kahkaha açısından iyileştir:\\n\\n{story_text}"
    },
    "ending-changer": {
        "system_role": "Sen bir hikaye sonu değiştirme uzmanısın.",
        "prompt_template": "Aşağıdaki hikayenin sonunu {ending_descriptions.get(ending_type, 'farklı bir sona')} değiştir:\n\n{story_text}"
    },
    "accuracy-checker": {
        "system_role": "Sen bir doğruluk kontrolü uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi doğruluk kontrolü açısından iyileştir:\\n\\n{story_text}"
    },
    "genre-converter": {
        "system_role": "Sen bir tür dönüştürme uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi tür dönüştürme açısından iyileştir:\\n\\n{story_text}"
    },
    "growth-marker": {
        "system_role": "Sen bir büyüme işareti uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi büyüme işareti açısından iyileştir:\\n\\n{story_text}"
    },
    "description-emotional": {
        "system_role": "Sen bir betimleme duygusal uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi betimleme duygusal açısından iyileştir:\\n\\n{story_text}"
    },
    "recommendation-engine": {
        "system_role": "Sen bir hikaye öneri uzmanısın.",
        "prompt_template": "Kullanıcı şu temalarda hikayeler okumuş: {themes_text}\nBu kullanıcıya benzer temalarda yeni hikaye önerileri yap."
    },
    "location-changer": {
        "system_role": "Sen bir mekan değiştirme uzmanısın.",
        "prompt_template": "Aşağıdaki hikayenin mekanını '{new_location}' olarak değiştir:\n\n{story_text}\n\nYeni mekana uygun detaylar ekle."
    },
    "plot-modifier": {
        "system_role": "Sen bir olay örgüsü değiştirme uzmanısın.",
        "prompt_template": "Aşağıdaki hikayenin olay örgüsünü değiştir:\n{modification_type}: {modification_details}\n\nHikaye:\n{story_text}"
    },
    "content-comparison": {
        "system_role": "Sen bir hikaye karşılaştırma uzmanısın.",
        "prompt_template": "Aşağıdaki iki hikayeyi karşılaştır:\n1. Benzerlikler\n2. Farklılıklar\n3. Güçlü yönler\n4. İyileştirme önerileri\n\nHikaye 1:\n{story1_text}\n\nHikaye 2:\n{story2_text}"
    },
    "character-voice": {
        "system_role": "Sen bir karakter sesi uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi karakter sesi açısından iyileştir:\\n\\n{story_text}"
    },
    "character-development": {
        "system_role": "Sen bir karakter geliştirme uzmanısın.",
        "prompt_template": "Aşağıdaki karakter için detaylı bir profil oluştur:\nİsim: {character_name}\nTür: {character_type}\n{f\"Açıklama: {initial_description}\" if initial_description else \"\"}\n\nŞunları ekle:\n1. Fiziksel özellikler\n2. Kişilik özellikleri\n3. Geçmiş ve arka plan\n4. Motivasyonlar ve hedefler\n5. Güçlü ve zayıf yönler"
    },
    "educational-content": {
        "system_role": "Sen bir eğitim uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi {subject} dersi için {grade_level} seviyesinde öğrenme materyali haline getir.\nŞunları ekle:\n1. Öğrenme hedefleri\n2. Anahtar kavramlar\n3. Sorular ve aktiviteler\n4. Değerlendirme ölçütleri\n\nHikaye:\n{story_text}"
    },
    "sentence-variety": {
        "system_role": "Sen bir cümle çeşitliliği uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi cümle çeşitliliği açısından iyileştir:\\n\\n{story_text}"
    },
    "dialogue-rhythm": {
        "system_role": "Sen bir diyalog ritmi uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi diyalog ritmi açısından iyileştir:\\n\\n{story_text}"
    },
    "dialogue-balance": {
        "system_role": "Sen bir diyalog dengesi uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi diyalog dengesi açısından iyileştir:\\n\\n{story_text}"
    },
    "mood-setter": {
        "system_role": "Sen bir ruh hali ayarlama uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi ruh hali ayarlama açısından iyileştir:\\n\\n{story_text}"
    },
    "metaphor-enhancer": {
        "system_role": "Sen bir metafor uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeye metaforlar ekle:\\n\\n{story_text}"
    },
    "lesson-enhancer": {
        "system_role": "Sen bir ders geliştirme uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi ders geliştirme açısından iyileştir:\\n\\n{story_text}"
    },
    "content-verification": {
        "system_role": "Sen bir içerik doğrulama uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi doğrula:\n1. Dilbilgisi hataları\n2. Tutarlılık kontrolü\n3. Mantık hataları\n4. Çocuklar için uygunluk\n\nHikaye:\n{story_text}\n\nHer kontrol için sonuç ver."
    },
    "balance-creator": {
        "system_role": "Sen bir denge yaratma uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi denge yaratma açısından iyileştir:\\n\\n{story_text}"
    },
    "transition-smoother": {
        "system_role": "Sen bir geçiş yumuşatma uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi geçiş yumuşatma açısından iyileştir:\\n\\n{story_text}"
    },
    "flow-creator": {
        "system_role": "Sen bir akış yaratma uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi akış yaratma açısından iyileştir:\\n\\n{story_text}"
    },
    "rhythm-flow": {
        "system_role": "Sen bir ritim akışı uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi ritim akışı açısından iyileştir:\\n\\n{story_text}"
    },
    "excellence-achiever": {
        "system_role": "Sen bir mükemmellik uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi mükemmellik açısından iyileştir:\\n\\n{story_text}"
    },
    "dialogue-impact": {
        "system_role": "Sen bir diyalog etkisi uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi diyalog etkisi açısından iyileştir:\\n\\n{story_text}"
    },
    "repetition-optimizer": {
        "system_role": "Sen bir tekrar optimizasyon uzmanısın.",
        "prompt_template": "Aşağıdaki hikayedeki gereksiz tekrarları azalt, gerekli tekrarları koru:\\n\\n{story_text}"
    },
    "continuity-checker": {
        "system_role": "Sen bir süreklilik kontrolü uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi süreklilik kontrolü açısından iyileştir:\\n\\n{story_text}"
    },
    "retention-optimizer": {
        "system_role": "Sen bir tutma optimizasyonu uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi tutma optimizasyonu açısından iyileştir:\\n\\n{story_text}"
    },
    "world-technology": {
        "system_role": "Sen bir dünya teknolojisi uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi dünya teknolojisi açısından iyileştir:\\n\\n{story_text}"
    },
    "active-voice": {
        "system_role": "Sen bir aktif ses uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi aktif ses açısından iyileştir:\\n\\n{story_text}"
    },
    "viral-features": {
        "system_role": "Sen bir sosyal medya içerik uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeden {content_type} formatında viral içerik oluştur.\nPaylaşılabilir, ilgi çekici ve akılda kalıcı olsun:\n\n{story_text}"
    },
    "setting-richness": {
        "system_role": "Sen bir mekan zenginliği uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi mekan zenginliği açısından iyileştir:\\n\\n{story_text}"
    },
    "test-creator": {
        "system_role": "Sen bir test yaratma uzmanısın.",
        "prompt_template": "Aşağıdaki hikayeyi test yaratma açısından iyileştir:\\n\\n{story_text}"
    }
}

# Manual additions for missing features
STORY_ENHANCEMENT_CONFIG.update({
    "comment-response": {
        "system_role": "Sen bir topluluk yöneticisisin.",
        "prompt_template": "Şu yoruma nazik, yapıcı ve etkileşimi artırıcı bir yanıt öner:\n\nYorum: {comment}\n{f'Bağlam: {story_context}' if story_context else ''}"
    },
    "viral-image-prompt": {
        "system_role": "Sen bir sosyal medya görsel uzmanısın.",
        "prompt_template": "Bu hikayeden paylaşılabilir bir söz (quote) seç ve görsel tasarımı tarif et.\n\nHikaye:\n{story_text}\n\nStil: {style}"
    }
})
