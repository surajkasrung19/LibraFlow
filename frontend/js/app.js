const API_URL = "/api/v1/books";

const booksTable = document.getElementById("books-table");
const bookForm = document.getElementById("book-form");
const message = document.getElementById("message");
const searchInput = document.getElementById("site-search");

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


