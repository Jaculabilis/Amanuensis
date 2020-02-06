function onContentChange() {
	// Get the new content
	var articleTitle = document.getElementById("editor-title").value;
	var articleBody = document.getElementById("editor-content").value;
	// Pass the draft text to the parser to get the preview html and citations
	var parseResult = parseLexipythonMarkdown(articleBody);
	// Build the citation block
	var citeTexts = []
	for (var i = 0; i < parseResult.citations.length; i++) {
		var cite = parseResult.citations[i];
		citeTexts.push("[" + cite.id.toString() + "] " + cite.citeTitle);
	}
	var citeblockContent = citeTexts.join(" / ");
	// Compute warnings and build the control block
	var flagMissingSignature = !parseResult.hasSignature;
	var wordCount = (parseResult.html
		// Delete all HTML tags
		.replace(/<[^>]+>/g, "")
		.trim()
		.split(/\s+/)
		.length);
	var controlContent = "";
	controlContent += "<p>Signature: " + (!flagMissingSignature).toString() + "</p>";
	controlContent += "<p>Word count: " + wordCount.toString() + "</p>";
	// Fill in the content blocks
	document.getElementById("preview").innerHTML = (
		"<h1>" + articleTitle + "</h1>\n"
		+ parseResult.html);
	document.getElementById("preview-citations").innerHTML = citeblockContent;
	document.getElementById("preview-control").innerHTML = controlContent;
}

function parseLexipythonMarkdown(text) {
	// Prepare return values
	var result = {
		html: "",
		citations: [],
		hasSignature: false,
	};
	// Parse the content by paragraph, extracting the citations
	var paras = text.trim().split(/\n\n+/);
	citationList = [];
	formatId = 1;
	for (var i = 0; i < paras.length; i++) {
		var para = paras[i];
		// Escape angle brackets
		para = para.replace(/</g, "&lt;");
		para = para.replace(/>/g, "&gt;");
		// Replace bold and italic marks with tags
		para = para.replace(/\/\/([^\/]+)\/\//g, "<i>$1</i>");
		para = para.replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>");
		// Replace \\LF with <br>LF
		para = para.replace(/\\\\\n/g, "<br>\n");
		// Abstract citations into the citation record
		linkMatch = para.match(/\[\[(([^|\[\]]+)\|)?([^|\[\]]+)\]\]/);
		while (linkMatch != null) {
			// Identify the citation text and cited article
			citeText = linkMatch[2] != null ? linkMatch[2] : linkMatch[3];
			citeTitle = linkMatch[3].charAt(0).toUpperCase() + linkMatch[3].slice(1);
			// Record the citation
			result.citations.push({
				id: formatId,
				citeText: citeText,
				citeTitle: citeTitle,
			});
			// Stitch the cite text in place of the citation, plus a cite number
			para =
				para.slice(0, linkMatch.index) +
				"<a href=\"#\">" +
				citeText +
				"</a>" +
				"<sup>" +
				formatId.toString() +
				"</sup>" +
				para.slice(linkMatch.index + linkMatch[0].length);
			formatId += 1; // Increment to the next format id
			linkMatch = para.match(/\[\[(([^|\[\]]+)\|)?([^|\[\]]+)\]\]/);
		}
		// Mark signature paragraphs with a classed span
		if (para.length > 0 && para[0] == "~") {
			para = "<hr><span class=\"signature\"><p>" + para.slice(1) + "</p></span>";
			result.hasSignature = true;
		} else {
			para = "<p>" + para + "</p>\n";
		}
		result.html += para;
	}
	if (citationList.length > 0) {
		content += "<p><i>The following articles will be cited:</i></p>\n";
		for (var i = 0; i < citationList.length; i++) {
			content += "<p>" + citationList[i] + "</p>\n";
		}
	}
	// Calculate approximate word count
	// var wordCount = text.trim().split(/\s+/).length;
	// if (text.trim().length < 1)
		// wordCount = 0;
	// content += "<p><i>Article length: approx. " + wordCount + " words</p>";

	return result;
}

// Parse the article content and update the preview pane


// function download() {
// 	var articlePlayer = document.getElementById("article-player").value;
// 	var articleTurn = document.getElementById("article-turn").value;
// 	var articleTitle = document.getElementById("article-title").value;
// 	var articleBody = document.getElementById("article-body").value;
// 	var articleText =
// 		"# Player: " + articlePlayer + "\n" +
// 		"# Turn: " + articleTurn + "\n" +
// 		"# Title: " + articleTitle + "\n" +
// 		"\n" +
// 		articleBody;
// 	var articleFilename = articleTitle.toLowerCase().replace(/[^a-z0-9- ]/g, "").replace(/ +/g, "-");
// 	var downloader = document.createElement("a");
// 	downloader.setAttribute("href", "data:text/plain;charset=utf-8," + encodeURIComponent(articleText));
// 	downloader.setAttribute("download", articleFilename);
// 	if (document.createEvent) {
// 		var event = document.createEvent("MouseEvents");
// 		event.initEvent("click", true, true);
// 		downloader.dispatchEvent(event);
// 	} else {
// 		downloader.click();
// 	}
// }

window.onload = function() {
	document.getElementById("editor-content").value = "\n\n" + params.defaultSignature;
	this.onContentChange();
};

window.addEventListener("beforeunload", function(e) {
	var content = document.getElementById("editor-content").value
	var hasText = content.length > 0 && content != "\n\n" + params.defaultSignature;
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