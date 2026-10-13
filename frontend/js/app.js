const API_URL = "/api/v1/books";

const booksTable = document.getElementById("books-table");
const bookForm = document.getElementById("book-form");
const message = document.getElementById("message");
const searchInput = document.getElementById("site-search");

const editDialog = document.getElementById("edit-dialog");
const editForm = document.getElementById("edit-book-form");
const editMessage = document.getElementById("edit-message");

const editTitle = document.getElementById("edit-title");
const editAuthor = document.getElementById("edit-author");
const editCategory = document.getElementById("edit-category");

const closeEditButton = document.getElementById("close-edit");
const cancelEditButton = document.getElementById("cancel-edit");
const saveEditButton = document.getElementById("save-edit");

let editingBookId = null;
let originalBookData = null;

let allBooks = [];


async function loadBooks() {
    try {
        const response = await fetch(API_URL);

        if (!response.ok) {
            throw new Error("Failed to load books");
        }

        const books = await response.json();

        allBooks = books;

        filterBooks();
        updateStats(allBooks);

    } catch (error) {
        message.textContent = error.message;
    }
}


function displayBooks(books) {
    //1.Clear previosuly displayed rows
    booksTable.replaceChildren();

        //2.handle an empty array
    if (books.length === 0) {
        const row = document.createElement("tr");
        const cell = document.createElement("td");

        cell.colSpan = 5;
        cell.textContent = "No books found matching your search.";
        cell.classList.add("empty-message");

        row.appendChild(cell);
        booksTable.appendChild(row);

        return;
    }

     //3. Display the matching books
    for (const book of books) {
        const row = document.createElement("tr");

        const values = [
            book.id,
            book.title,
            book.author,
            book.isbn,
            `${book.available_copies} / ${book.total_copies}`
        ];

        for (const value of values) {
            const cell = document.createElement("td");

            cell.textContent = value;
            row.appendChild(cell);
        }

        const actionCell = document.createElement("td");

        const editButton = document.createElement("button");

        editButton.type = "button";
        editButton.textContent = "Edit";
        editButton.classList.add("edit-btn");

        editButton.addEventListener("click", () => {
            openEditDialog(book);
        });

        const archiveButton = document.createElement("button");

        archiveButton.type = "button";
        archiveButton.textContent = "Archive";
        archiveButton.classList.add("archive-btn");

        archiveButton.addEventListener("click", () => {
            archiveBook(book);
        });


        actionCell.appendChild(editButton);
        actionCell.appendChild(archiveButton);
        
        
        row.appendChild(actionCell)
        booksTable.appendChild(row);
    }
}



function updateStats(books) {
    const totalCopies = books.reduce(
        (sum, book) => sum + book.total_copies,
        0
    );

    const availableCopies = books.reduce(
        (sum, book) => sum + book.available_copies,
        0
    );

    document.getElementById("total-books").textContent =
        books.length;

    document.getElementById("total-copies").textContent =
        totalCopies;

    document.getElementById("available-copies").textContent =
        availableCopies;
}


loadBooks();


bookForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const bookData = {
        title: document.getElementById("title").value.trim(),
        author: document.getElementById("author").value.trim(),
        isbn: document.getElementById("isbn").value.trim(),
        total_copies: Number(
            document.getElementById("total_copies").value
        )
    };

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(bookData)
        });

        const data = await response.json();

        if (!response.ok) {
            const detail = typeof data.detail === "string"
                ? data.detail
                : "Please check the book information";

            throw new Error(detail);
        }

        message.textContent = "Book added successfully!";

        bookForm.reset();

        await loadBooks();

    } catch (error) {
        message.textContent = error.message;
    }
});


function filterBooks() {
    const searchText = searchInput.value.trim().toLowerCase();

    const filteredBooks = allBooks.filter((book) => {
        const titleMatches = book.title
            .toLowerCase()
            .includes(searchText);

        const authorMatches = book.author
            .toLowerCase()
            .includes(searchText);

        return titleMatches || authorMatches;
    });

    displayBooks(filteredBooks);
}

searchInput.addEventListener("input", filterBooks);

function openEditDialog(book) {
    editingBookId = book.id;

    originalBookData = {
        title: book.title,
        author: book.author,
        category: book.category ?? ""
    }

    editTitle.value = originalBookData.title;
    editAuthor.value = originalBookData.author;
    editCategory.value = originalBookData.category ?? "";

    editMessage.textContent = "";

    editDialog.showModal();
}



function closeEditDialog() {
    editDialog.close();
    editingBookId = null;
    editMessage.textContent = "";
}

closeEditButton.addEventListener("click", closeEditDialog);

cancelEditButton.addEventListener("click", closeEditDialog);

editDialog.addEventListener("close", () => {
    editingBookId = null;
});



editForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (editingBookId === null) {
        return;
    }

    const updatedData = {
        title: editTitle.value.trim(),
        author: editAuthor.value.trim(),
        category: editCategory.value.trim() || null
    };

    try {
        saveEditButton.disabled = true;
        editMessage.textContent = "";

        const response = await fetch(
            `${API_URL}/${editingBookId}`,
            {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(updatedData)
            }
        );

        const data = await response.json();

        if (!response.ok) {
            const detail = typeof data.detail === "string"
                ? data.detail
                : "Unable to update book";

            throw new Error(detail);
        }

        editDialog.close();

        message.textContent = "Book updated successfully!";

        await loadBooks();

    } catch (error) {
        editMessage.textContent = error.message;
    } finally {
        saveEditButton.disabled = false;
    }
});


function hasUnsavedChanges() {
    if (!originalBookData) {
        return false
    }

    return (
        editTitle.value.trim() !== originalBookData.title ||
        editAuthor.value.trim() !== originalBookData.author ||
        editCategory.value.trim() !== originalBookData.category
    );
}

function resetEditState() {
    editingBookId = null;
    originalBookData = null;
    editMessage.textContent = "";
}


function requestCloseEditDialog() {
    if (hasUnsavedChanges()) {
        const confirmed = window.confirm(
            "You have unsaved changes. Discard them?"
        );

        if (!confirmed) {
            return;
        }
    }

    editDialog.close();
}


closeEditButton.addEventListener(
    "click",
    requestCloseEditDialog
);

cancelEditButton.addEventListener(
    "click",
    requestCloseEditDialog
);

editDialog.addEventListener("close", resetEditState);

editDialog.addEventListener("cancel", (event) => {
    event.preventDefault();

    requestCloseEditDialog();
});


async function archiveBook(book) {
    const confirmed = window.confirm(
        `Are you sure you want to archive "${book.title}"?`
    );

    if (!confirmed) {
        return;
    }

    try {
        const response = await fetch(
            `${API_URL}/${book.id}/archive`,
            {
                method: "PATCH"
            }
        );

        if (!response.ok) {
            const data = await response.json();

            throw new Error(
                typeof data.detail === "string"
                    ? data.detail
                    : "Failed to archive book"
            );
        }

        await loadBooks();

        message.textContent = "Book archived successfully!";

    } catch (error) {
        message.textContent = error.message;
    }
}