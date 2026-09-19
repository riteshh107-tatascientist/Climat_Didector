# ClimateGuard AI — 3-Minute Video Script

Tone: confident, direct, no hype-speak. Say what's true and let the working product carry it.

---

**0:00–0:20 — Problem**

"In India, flood, water-stress, and crop-stress risk data exists — but it's scattered across
meteorological, agricultural, and municipal sources, and it rarely gets translated into a
clear answer: *is this risky, why, and what do I do about it?* Most of the time, people find
out after the damage is already done."

**0:20–0:45 — Solution**

"ClimateGuard AI takes environmental readings — rainfall, temperature, soil, water storage —
and turns them into one thing: a risk score you can actually act on. Not a dashboard full of
raw numbers. A score, an explanation of what's driving it, and a specific recommendation.
One platform, three risk modules, one shared engine underneath."

**0:45–1:30 — Live product demo**

*(Screen recording, narrated live)*
"Let's try it. I'll pick Mumbai during monsoon season — heavy rainfall, high soil saturation,
weak drainage. I hit Analyze."
*(Result appears)*
"HIGH risk, score of 78. And here's the part that matters — it tells us why: heavy rainfall is
contributing the most, followed by poor drainage capacity and soil saturation. This isn't a
static rule — it's coming straight out of the trained model's own reasoning."
*(Scroll to recommendations)*
"And based on exactly those factors, it recommends activating flood-preparedness protocols
and prioritizing drainage — not generic advice, advice tied to what's actually driving this
specific score."

**1:30–2:00 — AI/ML + explainability**

"Underneath this is a real, trained scikit-learn pipeline — we compared Logistic Regression,
Random Forest, and Gradient Boosting for each module and kept the best one. Flood and water
models hit ROC-AUC around 0.81 to 0.82 on held-out test data. Every prediction comes with
ranked, signed factor contributions — SHAP where available, with a documented fallback
explainer otherwise — so the score is never a black box."

**2:00–2:30 — Impact**

"Every assessment is stored end-to-end: the inputs, the model version, the score, the
explanation, the recommendation. That means a real history you can search, filter, and audit
— not just a one-off prediction that disappears. And where we show projected impact, like
estimated water saved, we label it clearly as an estimate — we don't dress up a projection as
a measured result."

**2:30–2:50 — Scalability**

"The architecture is built to grow: new risk modules plug into the same risk engine without a
rewrite, and our data layer is designed so live IMD or NASA feeds can replace our current data
source with zero changes to the models or the API. This isn't a demo that stops working past
the pitch — it's a foundation."

**2:50–3:00 — Closing**

"ClimateGuard AI: real data, real models, real explanations, and a recommendation you can act
on before the risk becomes a loss. Thank you."
