let polling = false;

window.addEventListener('load', function () {
	console.log("Hello console log");
	document.getElementById('task_status').textContent = "Not started";
});

async function send_request_evaluate() {
	const doc = document.getElementById("document").value;
	const human_summary = document.getElementById("human_summary").value;

	try {
		const response = await fetch('/request', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				session_id: g_session_id,
				request: {
					type: "evaluate",
					document: doc,
					human_summary: human_summary
				}
			})
		});
		const result = await response.json();
		console.log("Evaluate:", result);

		// ✅ Update status display right after submission
		const statusElem = document.getElementById('task_status');
		if (result.status) {
			statusElem.textContent = result.status;
			startPolling()
		} else if (result.error) {
			statusElem.textContent = "Error: " + result.error;
		}

	} catch (e) {
		console.error("Exception during evaluation request:", e);
		document.getElementById('task_status').textContent = "Error submitting task";
	}
}


async function send_request_status() {
	try {
		const response = await fetch('/request', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				session_id: g_session_id,
				request: { type: "status" }
			})
		});
		const result = await response.json();
		console.log("Status:", result);

		const statusElem = document.getElementById('task_status');
		if (result.status) {
			statusElem.textContent = result.status;
		} else if (result.error) {
			statusElem.textContent = "Error: " + result.error;
		}
		return result.status;
	} catch (e) {
		console.error("Exception during status request:", e);
		document.getElementById('task_status').textContent = "Error checking status";
		return "error";
	}
}

async function send_request_results() {
	try {
		const response = await fetch('/request', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				session_id: g_session_id,
				request: { type: "results" }
			})
		});
		const result = await response.json();
		console.log("Results:", result);

		if (result.status === "success") {
			show_chart(result.results);
		} else {
			alert("Error: " + result.error);
		}
	} catch (e) {
		console.error("Exception during result request:", e);
	}
}

async function send_request_dataset_example() {
	try {
		const response = await fetch('/request', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				session_id: g_session_id,
				request: { type: "dataset_example" }
			})
		});
		const result = await response.json();
		console.log("Results:", result);

		// Go ahead and replace the two text boxes with the doc and summary
		if (result.status === "success") {
			document.getElementById('document').textContent = result.example.document;
			document.getElementById('human_summary').textContent = result.example.human_summary;
		} else {
			alert("Error: " + result.error);
		}
	} catch (e) {
		console.error("Exception during result request:", e);
	}
}

function show_chart(results) {
	const ctx = document.getElementById('results_chart').getContext('2d');
	document.getElementById('results_chart').style.display = 'block';

	if (window.resultChart) {
		window.resultChart.destroy();
	}

	window.resultChart = new Chart(ctx, {
		type: 'bar',
		data: {
			labels: results.map(r => r.label),
			datasets: [{
				label: 'Evaluation Score',
				data: results.map(r => r.value),
				backgroundColor: 'rgba(54, 162, 235, 0.6)'
			}]
		},
		options: {
			scales: {
				y: {
					beginAtZero: true,
					max: 1.0
				}
			}
		}
	});
}

function startPolling() {
	if (polling) return;
	polling = true;

	const intervalId = setInterval(async () => {
		const status = await send_request_status();

		if (status === "completed" || status === "failed" || status === "error") {
			clearInterval(intervalId);
			polling = false;

			if (status === "completed") {
				send_request_results(); // Auto-fetch results
			}
		}
	}, 10000); // Poll every 5 seconds
}
