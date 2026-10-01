from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class Detection:
    class_name: str
    confidence: float
    xyxy: tuple[float, float, float, float]
    mask: np.ndarray


class YoloSegmenter:
    def __init__(
        self,
        model_name: str = "yolo26n-seg.pt",
        confidence: float = 0.35,
        iou: float = 0.55,
        device: str | int | None = "auto",
    ) -> None:
        from ultralytics import YOLO

        self.model = YOLO(model_name)
        self.confidence = confidence
        self.iou = iou
        self.device = None if device == "auto" else device

    def __call__(self, image_bgr: np.ndarray) -> list[Detection]:
        result = self.model.predict(
            source=image_bgr,
            conf=self.confidence,
            iou=self.iou,
            device=self.device,
            verbose=False,
        )[0]

        if result.boxes is None or len(result.boxes) == 0:
            return []

        height, width = image_bgr.shape[:2]
        names = result.names
        masks_data = result.masks.data.cpu().numpy() if result.masks is not None else None
        detections: list[Detection] = []

        for idx, box in enumerate(result.boxes):
            cls_id = int(box.cls.item())
            confidence = float(box.conf.item())
            x1, y1, x2, y2 = map(float, box.xyxy[0].tolist())

            if masks_data is not None and idx < len(masks_data):
                raw_mask = masks_data[idx]
                if raw_mask.shape != (height, width):
                    raw_mask = cv2.resize(
                        raw_mask.astype(np.float32),
                        (width, height),
                        interpolation=cv2.INTER_NEAREST,
                    )
                mask = raw_mask > 0.5
            else:
                mask = np.zeros((height, width), dtype=bool)
                xi1 = max(0, min(width - 1, int(round(x1))))
                yi1 = max(0, min(height - 1, int(round(y1))))
                xi2 = max(0, min(width, int(round(x2))))
                yi2 = max(0, min(height, int(round(y2))))
                mask[yi1:yi2, xi1:xi2] = True

            detections.append(
                Detection(
                    class_name=str(names[cls_id]),
                    confidence=confidence,
                    xyxy=(x1, y1, x2, y2),
                    mask=mask,
                )
            )

        return detections
