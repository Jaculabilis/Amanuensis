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

// Initialize editor
window.onload = function() {
	document.getElementById("preview").innerHTML = "<p>&nbsp;</p>";

	if (params.article != null) {
		document.getElementById("editor-title").value = params.article.title;
		document.getElementById("editor-content").value = params.article.contents;
	}

	onContentChange();
};

function getArticleObj() {
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
	req.onreadystatechange = function () {
		if (req.readyState == 4 && req.status == 200) {
			params.article = article;
			document.getElementById("preview-control").innerHTML = JSON.stringify(req.response);
		}
	};
	req.send(JSON.stringify(article));
}

function onContentChange() {
	ifNoFurtherChanges(() => {
		var article = getArticleObj();
		update(article);
	});
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
			ifNoFurtherChanges(() => {
				var article = getArticleObj();
				update(article);
			}, 0);
		}
	}
});