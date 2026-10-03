import numpy as np

def predict_traffic(zone_id: str):
    # Simple prediction using numpy
    base_volume = np.random.normal(500, 100)
    predictions = []
    
    for i in range(24):
        # Add some diurnal pattern
        multiplier = 1.0 + 0.5 * np.sin(i * np.pi / 12 - np.pi / 2)
        pred_vol = max(0, int(base_volume * multiplier + np.random.normal(0, 20)))
        predictions.append({"hour_offset": i, "predicted_volume": pred_vol})
        
    confidence = float(np.clip(np.random.normal(0.85, 0.05), 0.6, 0.99))
    
    return {
        "zone_id": zone_id,
        "confidence_score": confidence,
        "predictions": predictions
    }
