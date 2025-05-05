window.addEventListener('load', function() {
	console.log("Hello console log");
})

async function send_request_evaluate()
{
	const doc = document.getElementById('document').value;
	const human_summary = document.getElementById('human_summary').value;
	try
	{
		const request = {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				session_id: g_session_id,
				request: {
					"type": "evaluate",
					"document": doc,
					"human_summary": human_summary, 
				},
			})
		};
		const response = await fetch('/request', request);
		const result = await response.text()
		console.log(result)
	}
	catch(e)
	{
		console.log("exception: ", e);
	}
}

async function send_request_results()
{
	try
	{
		const request = {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				"session_id": g_session_id,
				"request": {
					"type": "results",
				},
			})
		};
		const response = await fetch('/request', request);
		const result = await response.text()
		console.log(result)
	}
	catch(e)
	{
		console.log("exception: ", e);
	}
}

async function send_request_status()
{
	try
	{
		const request = {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				"session_id": g_session_id,
				"request": {
					"type": "status",
				},
			})
		};
		const response = await fetch('/request', request);
		const result = await response.text()
		console.log(result)
	}
	catch(e)
	{
		console.log("exception: ", e);
	}
}
