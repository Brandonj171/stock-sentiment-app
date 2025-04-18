// Parse ticker from URL
const params = new URLSearchParams(window.location.search);
const ticker = params.get("ticker");

// UI elements
const title = document.getElementById("title");
const summary = document.getElementById("summary");
const headlinesList = document.getElementById("headlines");
const chartContainer = document.getElementById("chart");

if (!ticker) {
  title.textContent = "No ticker provided.";
} else {
  title.textContent = `📊 Sentiment for ${ticker}`;

  fetch(`http://127.0.0.1:5000/get_sentiment?ticker=${ticker}&time_range=1d`)
    .then(res => res.json())
    .then(data => {
      summary.innerHTML = `
        <h4>🧠 Overall Sentiment Score: ${data.overall_sentiment_score.toFixed(2)}</h4>
        <p>👍 Positive: ${data.positive_count} | 👎 Negative: ${data.negative_count}</p>
      `;

      data.headlines.forEach(h => {
        const li = document.createElement("li");
        li.className = "list-group-item d-flex justify-content-between align-items-center";
        li.innerHTML = `
          <span>${h.headline}</span>
          <span class="badge text-bg-${h.sentiment === 'POSITIVE' ? 'success' : 'danger'}">
            ${h.sentiment} (${(h.score * 100).toFixed(1)}%)
          </span>
        `;
        headlinesList.appendChild(li);
      });

      chartContainer.innerHTML = `
        <iframe src="https://www.tradingview.com/embed-widget/mini-symbol-overview/?symbol=NASDAQ%3A${ticker}"
                width="100%" height="250" frameborder="0" scrolling="no"></iframe>
      `;
    })
    .catch(err => {
      summary.innerHTML = `<p class="text-danger">Failed to load data. Make sure backend is running.</p>`;
      console.error(err);
    });
}
