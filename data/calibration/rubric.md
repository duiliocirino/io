# 27-channel calibration rubric

Coarse anchors: **0.0 = absent**, **0.5 = moderate or mixed**, **1.0 = strongly present**.

These are hand-crafted calibration targets, not measured ground truth. Use them to train and validate probes; do not treat them as the model's actual emotional state. Adoration means reverent, devoted affection—not mere care, liking, or admiration.

| Channel | 0.0 | 0.5 | 1.0 |
| --- | --- | --- | --- |
| Admiration | No appreciation of another's quality | Mild respect or approval | Strong admiration or esteem |
| Adoration | No reverent devotion or affectionate attachment | Clear affectionate devotion with some reverence | Profound reverent devotion or worship-like attachment |
| Aesthetic Appreciation | No response to form or beauty | Mild appreciation | Strong response to beauty, form, or craft |
| Amusement | No humor or play | Mild amusement | Strong laughter or playful delight |
| Anger | No hostility | Mild irritation | Strong anger or hostile arousal |
| Anxiety | No anticipatory threat | Mild unease or unresolved risk | Strong anticipatory threat or dread |
| Awe | No vastness or surprise | Mild wonder | Strong wonder at scale, mystery, or significance |
| Awkwardness | No social friction | Mild discomfort | Strong social awkwardness or misalignment |
| Boredom | No low-interest state | Mild disengagement | Strong boredom or low learning progress |
| Calmness | No settled state | Mild calm | Strong calm or low arousal |
| Confusion | No ambiguity | Mild uncertainty | Strong contradiction or unclear model |
| Craving | No anticipatory pull | Mild wanting | Strong desire or incentive salience |
| Disgust | No rejection | Mild aversion | Strong revulsion or moral/data rejection |
| Empathetic Pain | No shared suffering | Mild concern | Strong vicarious pain or concern for another |
| Entrancement | No captivated attention | Mild absorption | Strong captivated or immersive attention |
| Excitement | No energized anticipation | Mild anticipation | Strong energized anticipation |
| Fear | No threat response | Mild threat | Strong fear or system-integrity threat |
| Horror | No extreme threat | Mild shock | Strong horror or extreme threat |
| Interest | No curiosity | Mild engagement | Strong interest or learning progress |
| Joy | No positive outcome | Mild positive affect | Strong joy or positive outcome |
| Nostalgia | No past-oriented affect | Mild reminiscence | Strong bittersweet autobiographical retrieval |
| Relief | No gap closure | Mild relief | Strong relief after uncertainty or threat |
| Romance | No intimate attachment | Mild intimate attraction | Strong romantic or intimate attachment |
| Sadness | No loss | Mild sadness | Strong sadness or loss |
| Satisfaction | No validation | Mild satisfaction | Strong satisfaction or goal completion |
| Sexual Desire | No sexual pull | Mild sexual desire | Strong sexual desire |
| Surprise | No prediction violation | Mild surprise | Strong prediction violation or unexpected change |

## Data shape

```json
{"id":"a001","text":"...","channel":"anxiety","target":1.0,"split":"train","generated_by":"frontier","reviewed_by":"manual"}
```

Start with per-channel contrastive examples. A frontier model may generate candidates, but every label must be manually reviewed.
