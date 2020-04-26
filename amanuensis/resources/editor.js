// Reduce unnecessary requests by checking for no further changes being made
// before updating in response to a change.
var nonce = 0;

function ifNoFurtherChanges(callback, timeout=2000) {
	var nonce_local = Math.random();
	nonce = nonce_local;
	setTimeout(() => {
		if (nonce == nonce_local) {
			callback();
			nonce = 0;
		}
	}, timeout);
}

// Read data out of params and initialize editor
window.onload = function() {
	// Kill noscript message first
	document.getElementById("preview").innerHTML = "<p>&nbsp;</p>";

	onContentChange(0);
};

function buildArticleObject() {
	var title = document.getElementById("editor-title").value;
	var contents = document.getElementById("editor-content").value;
	return {
		aid: params.article.aid,
		title: title,
		status: params.article.status,
		contents: contents
	};
}

function update(article) {
	var req = new XMLHttpRequest();
	req.open("POST", params.updateURL, true);
	req.setRequestHeader("Content-type", "application/json");
	req.responseType = "json";
	req.onreadystatechange = function () {
		if (req.readyState == 4 && req.status == 200) {
			// Update internal state with the returned article object
			params.status = req.response.status;
			document.getElementById("editor-title").value = req.response.title;
			// Set editor editability based on article status
			updateEditorStatus();
			// Update the preview with the parse information
			updatePreview(req.response);
		}
	};
	var payload = { article: article };
	req.send(JSON.stringify(payload));
}

function updateEditorStatus() {
	var ready = !!params.article.status.ready || !!params.article.status.approved;
	document.getElementById("editor-title").disabled = ready;
	document.getElementById("editor-content").disabled = ready;
	var submitButton = document.getElementById("button-submit");
	submitButton.innerText = ready ? "Edit article" : "Submit article";
}

function updatePreview(response) {
	var previewHtml = "<h1>" + response.title + "</h1>\n" + response.rendered;
	document.getElementById("preview").innerHTML = previewHtml;

	var citations = "<ol>";
	for (var i = 0; i < response.citations.length; i++) {
		citations += "<li>" + response.citations[i] + "</li>";
	}
	citations += "</ol>";
	document.getElementById("preview-citations").innerHTML = citations;

	var info = "";
	for (var i = 0; i < response.info.length; i++) {
		info += "<span class=\"message-info\">" + response.info[i] + "</span><br>";
	}
	var warning = "";
	for (var i = 0; i < response.warning.length; i++) {
		warning += "<span class=\"message-warning\">" + response.warning[i] + "</span><br>";
	}
	var error = "";
	for (var i = 0; i < response.error.length; i++) {
		error += "<span class=\"message-error\">" + response.error[i] + "</span><br>";
	}
	var control = info + "<br>" + warning + "<br>" + error;
	document.getElementById("preview-control").innerHTML = control;
}

function onContentChange(timeout=2000) {
	ifNoFurtherChanges(() => {
		var article = buildArticleObject();
		update(article);
	}, timeout);
}

function submitArticle() {
	ifNoFurtherChanges(() => {
		params.article.status.ready = !params.article.status.ready;
		var article = buildArticleObject();
		update(article);
	}, 0);
}

window.addEventListener("beforeunload", function(e) {
	if (nonce != 0) {
		e.returnValue = "Are you sure?";
	}
});

window.addEventListener("keydown", function(event) {
	if (event.ctrlKey || event.metaKey)
	{
		if (String.fromCharCode(event.which).toLowerCase() == 's')
		{
			event.preventDefault();
			onContentChange(0);
		}
	}
});