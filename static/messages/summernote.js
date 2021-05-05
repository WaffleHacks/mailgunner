// Load a list of emojis
$.ajax({
    url: "https://api.github.com/emojis",
    async: false
}).then(data => {
    window.emojis = Object.keys(data);
    window.emojiUrls = data;
});

// Convert a html string to text
const asText = html => html
    .replace(/<style([\s\S]*?)<\/style>/gi, "")
    .replace(/<script([\s\S]*?)<script\/>/gi, "")
    .replace(/<\/div>/gi, "\n")
    .replace(/<\/li>/gi, "\n")
    .replace(/<li>/gi, " * ")
    .replace(/<\/ul>/gi, "\n")
    .replace(/<\/p>/gi, "\n")
    .replace(/<[^>]+>/gi, "");

$(document).ready(function() {
    // Initialize the editor
    const summernote = $("#summernote");
    summernote.summernote({
        height: 300,
        minHeight: 300,
        tabsize: 2,
        dialogsInBody: true,
        toolbar: [
            ['style', ['style']],
            ['font', ['bold', 'underline', 'clear']],
            ['fontname', ['fontname', 'fontsize']],
            ['color', ['forecolor', 'backcolor']],
            ['para', ['ul', 'ol', 'paragraph']],
            ['table', ['table']],
            ['insert', ['link', 'picture', 'video', 'hr']],
            ['view', ['fullscreen', 'codeview', 'help']],
        ],
        hint: {
            match: /:([\-+\w]+)$/,
            search: (keyword, callback) => callback($.grep(emojis, item => item.indexOf(keyword) === 0)),
            template: item => `<img src="${emojiUrls[item]}" width="20" alt="${item} emoji"/> :${item}:`,
            content: item => emojiUrls[item] ? $("<img/>").attr("src", emojiUrls[item]).attr("alt", item + " emoji").css("width", 20)[0] : "",
        }
    });

    // Make background color slightly darker to be able to see the table
    $(".note-editable").css("background-color", "#ddd");

    // Add a plaintext component to the submission
    $("#message-form").on("submit", onSubmit);
});

function onSubmit() {
    // Convert the html to plain text
    const rawHtml = $("#summernote").summernote("code");
    const plaintext = asText(rawHtml);

    // Set the plaintext as a form element
    $("#plaintext").val(plaintext);
}
