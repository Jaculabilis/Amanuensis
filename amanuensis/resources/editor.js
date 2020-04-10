// Reduce unnecessary requests by checking for no further changes being made
// before updating in response to a change.
var nonce = 0;

function ifNoFurtherChanges(callback, timeout=2000) {
	var nonce_local = Math.random();
	nonce = nonce_local;
	setTimeout(() => {
		if (nonce == nonce_local) {
			callback()
		}
	}, timeout);
}

// Read data out of params and initialize editor
window.onload = function() {
	// Kill noscript message first
	document.getElementById("preview").innerHTML = "<p>&nbsp;</p>";

	if (params.article != null) {
		document.getElementById("editor-title").value = params.article.title;
		document.getElementById("editor-content").value = params.article.contents;
	}

	onContentChange(0);
};

function buildArticleObject() {
	var title = document.getElementById("editor-title").value;
	var contents = document.getElementById("editor-content").value;
	return {
		aid: params.article.aid,
		lexicon: params.article.lexicon,
		character: params.article.character,
		title: title,
		turn: params.article.turn,
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
			params.article = req.response.article;
			// Set editor editability based on article status
			updateEditorStatus();
			// Update the preview with the parse information
			updatePreview(req.response.info);
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

function updatePreview(info) {
	var title = document.getElementById("editor-title").value;
	var previewHtml = "<h1>" + title + "</h1>\n" + info.rendered;
	document.getElementById("preview").innerHTML = previewHtml;
	document.getElementById("preview-control").innerHTML = info.word_count;
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
	var content = document.getElementById("editor-content").value
	var hasText = content.length > 0 && content != params.article.contents;
	if (hasText) {
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