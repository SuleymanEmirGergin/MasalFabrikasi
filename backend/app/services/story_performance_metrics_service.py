from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime, timedelta


class StoryPerformanceMetricsService:
    """Hikaye performans ve metrikler servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.metrics_file = os.path.join(settings.STORAGE_PATH, "story_metrics.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.metrics_file):
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    async def track_story_performance(
        self,
        story_id: str,
        metric_type: str,
        value: float,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Hikaye performansını takip eder."""
        metrics = self._load_metrics()
        
        if story_id not in metrics:
            metrics[story_id] = {
                "story_id": story_id,
                "metrics": {},
                "timeline": []
            }
        
        timestamp = datetime.now().isoformat()
        
        # Metrik kaydı
        if metric_type not in metrics[story_id]["metrics"]:
            metrics[story_id]["metrics"][metric_type] = []
        
        metric_entry = {
            "value": value,
            "timestamp": timestamp,
            "metadata": metadata or {}
        }
        
        metrics[story_id]["metrics"][metric_type].append(metric_entry)
        metrics[story_id]["timeline"].append({
            "metric_type": metric_type,
            "value": value,
            "timestamp": timestamp
        })
        
        self._save_metrics(metrics)
        
        return {
            "message": "Metrik kaydedildi",
            "metric_type": metric_type,
            "value": value
        }
    
    async def get_story_performance(
        self,
        story_id: str,
        metric_types: Optional[List[str]] = None
    ) -> Dict:
        """Hikaye performansını getirir."""
        metrics = self._load_metrics()
        story_metrics = metrics.get(story_id, {})
        
        if not story_metrics:
            return {
                "story_id": story_id,
                "message": "Metrik bulunamadı"
            }
        
        performance_data = {
            "story_id": story_id,
            "metrics": {}
        }
        
        metric_data = story_metrics.get("metrics", {})
        
        if metric_types:
            metric_data = {k: v for k, v in metric_data.items() if k in metric_types}
        
        for metric_type, values in metric_data.items():
            if values:
                performance_data["metrics"][metric_type] = {
                    "current": values[-1]["value"],
                    "average": sum(v["value"] for v in values) / len(values),
                    "max": max(v["value"] for v in values),
                    "min": min(v["value"] for v in values),
                    "count": len(values)
                }
        
        return performance_data
    
    async def get_performance_insights(
        self,
        story_id: str
    ) -> Dict:
        """Performans içgörüleri oluşturur."""
        metrics = self._load_metrics()
        story_metrics = metrics.get(story_id, {})
        
        if not story_metrics:
            return {"message": "Metrik bulunamadı"}
        
        # Son 7 günün metriklerini al
        cutoff = datetime.now() - timedelta(days=7)
        recent_metrics = [
            m for m in story_metrics.get("timeline", [])
            if datetime.fromisoformat(m["timestamp"]) >= cutoff
        ]
        
        # Trend analizi
        trends = {}
        for metric_type in set(m["metric_type"] for m in recent_metrics):
            type_metrics = [m for m in recent_metrics if m["metric_type"] == metric_type]
            if len(type_metrics) >= 2:
                first_half = type_metrics[:len(type_metrics)//2]
                second_half = type_metrics[len(type_metrics)//2:]
                
                first_avg = sum(m["value"] for m in first_half) / len(first_half)
                second_avg = sum(m["value"] for m in second_half) / len(second_half)
                
                if second_avg > first_avg * 1.1:
                    trends[metric_type] = "increasing"
                elif second_avg < first_avg * 0.9:
                    trends[metric_type] = "decreasing"
                else:
                    trends[metric_type] = "stable"
        
        return {
            "story_id": story_id,
            "trends": trends,
            "recent_activity": len(recent_metrics),
            "insights": self._generate_insights(story_metrics, trends)
        }
    
    def _generate_insights(self, metrics: Dict, trends: Dict) -> List[str]:
        """İçgörüler oluşturur."""
        insights = []
        
        if "views" in trends and trends["views"] == "increasing":
            insights.append("Hikayenizin görüntülenme sayısı artıyor!")
        
        if "engagement" in trends and trends["engagement"] == "increasing":
            insights.append("Kullanıcı etkileşimi yükseliyor.")
        
        if "shares" in metrics.get("metrics", {}):
            share_count = len(metrics["metrics"]["shares"])
            if share_count > 10:
                insights.append(f"Hikayeniz {share_count} kez paylaşıldı!")
        
        return insights
    
    def _load_metrics(self) -> Dict:
        """Metrikleri yükler."""
        try:
            with open(self.metrics_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_metrics(self, metrics: Dict):
        """Metrikleri kaydeder."""
        with open(self.metrics_file, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2)

