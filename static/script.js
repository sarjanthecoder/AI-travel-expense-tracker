function triggerFlightAndEstimate() {
  const sound = document.getElementById("flySound");
  const resultBox = document.getElementById("result");

  // Play flight sound
  sound.currentTime = 0;
  sound.play();

  // Remove default message if exists
  const defaultMsg = document.getElementById("default-msg");
  if (defaultMsg) defaultMsg.remove();

  // Show loading animation
  resultBox.innerHTML = `
    <div style="text-align:center;">
      <img src="https://i.gifer.com/ZZ5H.gif" alt="Loading..." style="width:60px;height:60px;">
      <p><b>Estimating your travel expenses...</b></p>
    </div>
  `;

  // Slight delay for realism, then run actual estimate
  setTimeout(getGeminiEstimate, 1500);
}

async function getGeminiEstimate() {
  const form = document.getElementById("travel-form");
  const resultBox = document.getElementById("result");

  const formData = new FormData(form);
  const payload = Object.fromEntries(formData.entries());

  try {
    const res = await fetch("/plan-trip", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const result = await res.json();

    if (result.error) {
      resultBox.innerHTML = "<b>Error:</b> " + result.error;
    } else {
      const currency = result.currency || "₹";
      const suggestions = result.suggestions || [];

      resultBox.innerHTML = `
        ✈️ <b>Flight:</b> ${currency}${result.flight}<br>
        🍽️ <b>Food:</b> ${currency}${result.food}<br>
        🏨 <b>Stay:</b> ${currency}${result.stay}<br>
        🎉 <b>Fun/Enjoyment:</b> ${currency}${result.entertainment}<br>
        💰 <b>Total Cost:</b> ${currency}${result.total_cost}<br>

        👥 <b>Per Person:</b> ${currency}${result.per_person}<br><br>
        🧳 <b>AI Suggestions for Destination:</b><br>
        ${suggestions.map(item => `🔹 ${item}`).join("<br>")}
      `;
    }
  } catch (err) {
    resultBox.innerHTML = "<b>Something went wrong:</b> " + err.message;
  }

  form.reset(); // optional
}
