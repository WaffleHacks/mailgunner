let fileIndex = 1;

// Register initial handlers
window.onload = () => {
    document.getElementById("add-attachment").onclick = addAttachment;
    document.getElementById("remove-attachment-1").onclick = removeAttachment(fileIndex);
    document.getElementById("message-cancel").onclick = () => history.back();
};

// Add an attachment row to the DOM
function addAttachment() {
    // Increment the current file to keep them unique
    fileIndex++;

    const container = document.getElementById("attachment-list");

    // Construct the child
    const listElement = document.createElement("li");
    listElement.className = "list-group-item";
    listElement.id = `attachment-${fileIndex}`;
    container.appendChild(listElement);

    // Add the row
    const row = document.createElement("div");
    row.className = "row";
    listElement.appendChild(row);

    // Add the first column
    const fileColumn = document.createElement("div");
    fileColumn.classList.add("col-md-10");
    fileColumn.classList.add("col-sm-12");
    row.appendChild(fileColumn);

    // Add the file input to the first column
    const fileInput = document.createElement("input");
    fileInput.type = "file";
    fileInput.className = "form-control";
    fileInput.name = `attachment-${fileIndex}`;
    fileColumn.appendChild(fileInput);

    // Add the second column
    const buttonColumn = document.createElement("div");
    buttonColumn.classList.add("col-md-2");
    buttonColumn.classList.add("col-sm-12");
    row.appendChild(buttonColumn);

    // Add the remove button to the button column
    const removeButton = document.createElement("button");
    removeButton.type = "button";
    removeButton.classList.add("btn");
    removeButton.classList.add("btn-outline-danger");
    removeButton.id = `remove-attachment-${fileIndex}`;
    removeButton.innerText = "Remove";
    removeButton.onclick = removeAttachment(fileIndex);
    buttonColumn.appendChild(removeButton);
}

// Remove an attachment row from the DOM
const removeAttachment = index => () => {
    // Get the specified element
    const element = document.getElementById(`attachment-${index}`);

    // Remove it from the DOM
    element.parentNode.removeChild(element);
};
