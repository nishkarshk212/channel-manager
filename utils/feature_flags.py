from typing import Dict

class FeatureFlags:
    def __init__(self):
        self._features = {
            "auto_caption": True,
            "ai_suggestions": False,
            "watermark": True,
            "auto_hashtag": True,
            "force_subscribe": True,
            "analytics_dashboard": True
        }

    def is_enabled(self, feature_name: str) -> bool:
        return self._features.get(feature_name, False)

    def toggle(self, feature_name: str):
        if feature_name in self._features:
            self._features[feature_name] = not self._features[feature_name]

    def get_all(self) -> Dict[str, bool]:
        return self._features

features = FeatureFlags()
