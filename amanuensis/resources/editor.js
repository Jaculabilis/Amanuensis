// Editor state
var loadedArticleInfo = {
	aid: null,
	lexicon: null,
	character: null,
	title: null,
	turn: null,
	status: {
		ready: null,
		approved: null,
	},
	contents: null,
};

// Reduce unnecessary requests by checking for no further changes being made
// before updating in response to a change.
var nonce = 0;

function ifNoFurtherChanges(callback) {
	var nonce_local = Math.random();
	nonce = nonce_local;
	setTimeout(() => {
		if (nonce == nonce_local) {
			callback()
		}
	}, 2500);
}

// Initialize editor
window.onload = function() {
	loadedArticleInfo.character = params.characterId;

	document.getElementById("preview").innerHTML = "<p>&nbsp;</p>";

	// document.getElementById("editor-content").value = "\n\n" + params.default_signature;
	
	// this.onContentChange();
};

function getArticleObj() {
	// aid
	// lexicon
	// character
	// title
	// turn
	// status
	// contents
}

function update(article) {
	var req = new XMLHttpRequest();
	req.open("POST", params.updateURL, true);
	req.setRequestHeader("Content-type", "application/json");
	req.onreadystatechange = function () {
		if (req.readyState == 4 && req.status == 200)
			return;
	};
	req.send(article)
}

function onContentChange() {
	setTimeout(() => {
		if (nonce == nonce_local) {
			// Get the new content
			var articleTitle = document.getElementById("editor-title").value;
			var articleBody = document.getElementById("editor-content").value;
			// Pass the draft text to the parser to get the preview html and citations
			var parseResult = parseLexipythonMarkdown(articleBody);
			// Build the citation block
			var citeblockContent = makeCiteblock(parseResult);
			// Compute warnings and build the control block
			var controlContent = checkWarnings(parseResult);
			// Fill in the content blocks
			document.getElementById("preview").innerHTML = (
				"<h1>" + articleTitle + "</h1>\n"
				+ parseResult.html);
			document.getElementById("preview-citations").innerHTML = citeblockContent;
			document.getElementById("preview-control").innerHTML = controlContent;
		}
	}, 3000);
}

window.addEventListener("beforeunload", function(e) {
	var content = document.getElementById("editor-content").value
	var hasText = content.length > 0 && content != "\n\n" + params.default_signature;
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
			document.getElementById("preview").innerHTML += "<p>wrong</p>";
		}
	}
});