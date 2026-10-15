const API_URL = "/api/v1/books";
const MEMBERS_API_URL = "/api/v1/members";

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

//member
const memberForm = document.getElementById("member-form");
const memberName = document.getElementById("member-name");
const memberEmail = document.getElementById("member-email");
const memberPhone = document.getElementById("member-phone");

const membersTable = document.getElementById("members-table");
const memberMessage = document.getElementById("member-message");
const memberCount = document.getElementById("member-count");
const memberSearch = document.getElementById("member-search");
const registerMemberButton = document.getElementById(
    "register-member-btn"
);

const editMemberDialog = document.getElementById("edit-member-dialog");
const editMemberForm = document.getElementById("edit-member-form");

const editMemberName = document.getElementById("edit-member-name");
const editMemberEmail = document.getElementById("edit-member-email");
const editMemberPhone = document.getElementById("edit-member-phone");

const editMemberMessage = document.getElementById("edit-member-message");
const saveMemberButton = document.getElementById("save-member-edit");

const closeMemberEditButton = document.getElementById("close-member-edit");
const cancelMemberEditButton = document.getElementById("cancel-member-edit");

let editingMemberId = null;


let editingBookId = null;
let originalBookData = null;

let allBooks = [];
let allMembers = [];


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


//members
async function loadMembers() {
    try {
        const response = await fetch(MEMBERS_API_URL);

        if (!response.ok) {
            throw new Error("Failed to load members");
        }

        allMembers = await response.json();

        memberCount.textContent =
            `Active Members: ${allMembers.length}`;

        filterMembers();

    } catch (error) {
        memberMessage.textContent = error.message;
    }
}

function displayMembers(members) {
    membersTable.replaceChildren();

    if (members.length === 0) {
        const row = document.createElement("tr");
        const cell = document.createElement("td");

        cell.colSpan = 5;
        cell.textContent = "No members found.";

        row.appendChild(cell);
        membersTable.appendChild(row);

        return;
    }

    for (const member of members) {
        const row = document.createElement("tr");

        const values = [
            member.id,
            member.full_name,
            member.email,
            member.phone ?? "Not provided"
        ];

        for (const value of values) {
            const cell = document.createElement("td");

            cell.textContent = String(value);
            row.appendChild(cell);
        }

        const actionCell = document.createElement("td");

        //Flex container for action buttons
        const actionWrapper = document.createElement("div");
        actionWrapper.classList.add("member-actions");
        
        //Edit button
        const editButton = document.createElement("button");
        editButton.type = "button";
        editButton.textContent = "Edit";
        editButton.classList.add("edit-btn");

        editButton.addEventListener("click", () => {
            openMemberEditDialog(member);
        });

        actionCell.appendChild(editButton);

        //Deactivate Button
        const deactivateButton = document.createElement("button");

        deactivateButton.type = "button";
        deactivateButton.textContent = "Deactivate";
        deactivateButton.classList.add("deactivate-btn");

        deactivateButton.addEventListener("click", () => {
            deactivateMember(member, deactivateButton);
        });
        
        // Add both buttons to the same wrapper
        actionWrapper.appendChild(editButton);
        actionWrapper.appendChild(deactivateButton);

        actionCell.appendChild(actionWrapper);

        row.appendChild(actionCell);
        membersTable.appendChild(row);
    }
}

function filterMembers() {
    const searchText = memberSearch.value.trim().toLowerCase();

    const filteredMembers = allMembers.filter((member) => {
        const nameMatches = member.full_name
            .toLowerCase()
            .includes(searchText);

        const emailMatches = member.email
            .toLowerCase()
            .includes(searchText);

        return nameMatches || emailMatches;
    });

    displayMembers(filteredMembers);
}

memberSearch.addEventListener("input", filterMembers);


memberForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    console.log("Member registration form submitted!");

    const memberData = {
        full_name: memberName.value.trim(),
        email: memberEmail.value.trim(),
        phone: memberPhone.value.trim() || null
    };

    try {
        registerMemberButton.disabled = true;
        memberMessage.textContent = "";

        const response = await fetch(MEMBERS_API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(memberData)
        });

        const data = await response.json();

        if (!response.ok) {
            const errorText = typeof data.detail === "string"
                ? data.detail
                : "Unable to register member";

            throw new Error(errorText);
        }

        memberForm.reset();

        memberMessage.textContent =
            "Member registered successfully!";

        await loadMembers();

    } catch (error) {
        memberMessage.textContent = error.message;

    } finally {
        registerMemberButton.disabled = false;
    }
});

function openMemberEditDialog(member) {
    editingMemberId = member.id;

    editMemberName.value = member.full_name;
    editMemberEmail.value = member.email;
    editMemberPhone.value = member.phone ?? "";

    editMemberMessage.textContent = "";

    editMemberDialog.showModal();
}

function closeMemberEditDialog() {
    editMemberDialog.close();
    editingMemberId = null;
    editMemberMessage.textContent = "";
}

closeMemberEditButton.addEventListener("click", closeMemberEditDialog);
cancelMemberEditButton.addEventListener("click", closeMemberEditDialog);

editMemberDialog.addEventListener("close", () => {
    editingMemberId = null;
});

editMemberForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (editingMemberId === null) {
        return;
    }

    const updatedData = {
        full_name: editMemberName.value.trim(),
        email: editMemberEmail.value.trim(),
        phone: editMemberPhone.value.trim() || null
    };

    try {
        saveMemberButton.disabled = true;
        editMemberMessage.textContent = "";

        const response = await fetch(
            `${MEMBERS_API_URL}/${editingMemberId}`,
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
            throw new Error(
                typeof data.detail === "string"
                    ? data.detail
                    : "Failed to update member"
            );
        }

        editMemberDialog.close();
        editingMemberId = null;

        memberMessage.textContent = "Member updated successfully!";

        await loadMembers();

    } catch (error) {
        editMemberMessage.textContent = error.message;
    } finally {
        saveMemberButton.disabled = false;
    }
});

async function deactivateMember(member, button) {
    //1. Ask for confirmation
    const confirmed = window.confirm(
        `Are you sure you want to deactivate "${member.full_name}"?`
    );

    if (!confirmed) {
        return;
    }

    try {
        //2.Diable button while request is processing 
        button.diabled - true;
        memberMessage.textContent = "";

        //3. Send request to FastAPI
        const response = await fetch(
            `${MEMBERS_API_URL}/${member.id}/deactivate`,
            {
                method:"PATCH"
            }
        );

        //4.Check for API errors
        if (!response.ok) {
            const data = await response.json();

            throw new Error(
                typeof data.detail === "string"
                ? data.detail
                : "Failed to deactivate member"
            );
        }

        //5. Refresh the member list
        await loadMembers();

        //6. Display success message
        memberMessage.textContent = 
            `${member.full_name} has been deactivated successfully!`;
    
    } catch (error) {
        memberMessage.textContent = error.message;
        console.error("Member deactivation failed:", error);
    
    } finally {
        button.disabled = false
    }
}



loadBooks();
loadMembers();