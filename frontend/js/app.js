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

let allLoanHistory = [];
const MAX_LOAN_RENEWALS = 1;


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
        button.disabled = true;
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


async function loadLoanMembers() {
  const memberSelect = document.getElementById("loan-member");

  try {
    const response = await fetch("/api/v1/members");

    if (!response.ok) {
      throw new Error("Unable to load members");
    }

    const members = await response.json();

    memberSelect.replaceChildren(
      new Option("Choose a member", "")
    );

    members.forEach((member) => {
      const option = new Option(
        `${member.full_name} (${member.email})`,
        String(member.id)
      );

      memberSelect.add(option);
    });
  } catch (error) {
    console.error("Failed to load loan members:", error);
    showLoanMessage(error.message, true);
  }
}


async function loadLoanBooks() {
  const bookSelect = document.getElementById("loan-book");

  try {
    const response = await fetch("/api/v1/books");

    if (!response.ok) {
      throw new Error("Unable to load books");
    }

    const books = await response.json();

    bookSelect.replaceChildren(
      new Option("Choose a book", "")
    );

    books
      .filter((book) => book.available_copies > 0)
      .forEach((book) => {
        const option = new Option(
          `${book.title} — ${book.available_copies} available`,
          String(book.id)
        );

        bookSelect.add(option);
      });
  } catch (error) {
    console.error("Failed to load loan books:", error);
    showLoanMessage(error.message, true);
  }
}


function showLoanMessage(message, isError = false) {
  const messageElement = document.getElementById("loan-message");

  messageElement.textContent = message;
  messageElement.style.color = isError ? "#dc2626" : "#15803d";
}


async function handleBorrowSubmit(event) {
  event.preventDefault();

  const memberSelect = document.getElementById("loan-member");
  const bookSelect = document.getElementById("loan-book");
  const submitButton = document.getElementById("borrow-submit-btn");

  const memberId = Number(memberSelect.value);
  const bookId = Number(bookSelect.value);

  if (!memberId || !bookId) {
    showLoanMessage("Please select a member and a book.", true);
    return;
  }

  submitButton.disabled = true;
  showLoanMessage("Issuing book...");

  try {
    const response = await fetch("/api/v1/loans", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        member_id: memberId,
        book_id: bookId
      })
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(
        typeof result.detail === "string"
          ? result.detail
          : "Failed to issue book"
      );
    }

    document.getElementById("borrow-form").reset();

    // Refresh dropdown inventory
    await Promise.all([
        loadLoanBooks(),
        loadBooks(),
        loadActiveLoans(),
        loadLoanHistory()
    ]);


    showLoanMessage(
      `Book issued successfully! Loan #${result.id}`
    );
  } catch (error) {
    showLoanMessage(error.message, true);
  } finally {
    submitButton.disabled = false;
  }
}


async function initializeLoanManagement() {
  const borrowForm = document.getElementById("borrow-form");

  const refreshButton = document.getElementById(
    "refresh-loans-btn"
  );

  if (!borrowForm) return;

    //Register borrowing form listener
  borrowForm.addEventListener("submit", handleBorrowSubmit);

  //Register search and status filter listeners ONCE
  initializeLoanHistory();

  if (refreshButton) {
    refreshButton.addEventListener("click", async () => {
      refreshButton.disabled = true;

      try {
        await Promise.all([
            loadActiveLoans(),
            loadLoanMembers(),
            loadLoanBooks(),
            loadLoanHistory()
          ]);

        } catch (error) {
          console.error("Loan refresh error:", error);
        } finally {
          refreshButton.disabled = false;
        }
      });
    }

    await Promise.all([
      loadLoanMembers(),
      loadLoanBooks(),
      loadActiveLoans(),
      loadLoanHistory()
    ]);
  }


async function loadActiveLoans() {
  const tbody = document.getElementById("active-loans-body");

  if (!tbody) return;

  try {
    const [loansResponse, membersResponse, booksResponse] =
      await Promise.all([
        fetch("/api/v1/loans"),
        fetch("/api/v1/members"),
        fetch("/api/v1/books")
      ]);

    if (
      !loansResponse.ok ||
      !membersResponse.ok ||
      !booksResponse.ok
    ) {
      throw new Error("Failed to load loan information");
    }

    const loans = await loansResponse.json();
    const members = await membersResponse.json();
    const books = await booksResponse.json();

    const memberMap = new Map(
      members.map(member => [member.id, member.full_name])
    );

    const bookMap = new Map(
      books.map(book => [book.id, book.title])
    );

    const activeLoans = loans.filter(
      loan => loan.status === "borrowed"
    );

    const returnedLoans = loans.filter(
      loan => loan.status === "returned"
    );

    const now = new Date();

    const overdueLoans = activeLoans.filter(
      loan => new Date(loan.due_at) < now
    );

    document.getElementById("active-loans-count").textContent =
      activeLoans.length;

    document.getElementById("overdue-loans-count").textContent =
      overdueLoans.length;

    document.getElementById("returned-loans-count").textContent =
      returnedLoans.length;

    renderActiveLoans(activeLoans, memberMap, bookMap);

  } catch (error) {
    console.error("Error loading loans:", error);

    tbody.replaceChildren();

    const row = tbody.insertRow();
    const cell = row.insertCell();

    cell.colSpan = 7;
    cell.textContent = "Unable to load loans. Please retry.";

    showLoanMessage(error.message, true);
  }
}


function formatLoanDate(value) {
  if (!value) return "—";

  // SQLite may return a UTC datetime without a timezone suffix.
  const normalized = /(?:Z|[+-]\d{2}:\d{2})$/i.test(value)
    ? value
    : `${value}Z`;

  const date = new Date(normalized);

  return Number.isNaN(date.getTime())
    ? "Invalid date"
    : date.toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric"
      });
}

function renderActiveLoans(loans, memberMap, bookMap) {
  const tbody = document.getElementById("active-loans-body");

  if (!tbody) return;

  tbody.replaceChildren();

  if (loans.length === 0) {
    const row = tbody.insertRow();
    const cell = row.insertCell();

    cell.colSpan = 8;
    cell.textContent = "No active loans yet.";
    return;
  }

  loans.forEach(loan => {
    const row = tbody.insertRow();

    const memberName =
      memberMap.get(loan.member_id) ?? `Member #${loan.member_id}`;

    const bookTitle =
      bookMap.get(loan.book_id) ?? `Book #${loan.book_id}`;

    const displayStatus = getLoanDisplayStatus(loan);

    const values = [
      loan.id,
      memberName,
      bookTitle,
      formatLoanDate(loan.borrowed_at),
      formatLoanDate(loan.due_at),
      `${loan.renewal_count ?? 0} / ${MAX_LOAN_RENEWALS}`,
      displayStatus === "overdue" ? "Overdue" : "Borrowed"
    ];

    values.forEach(value => {
      const cell = row.insertCell();
      cell.textContent = String(value);
    });

    const actionCell = row.insertCell();

    const actionWrapper = document.createElement("div");
    actionWrapper.className = "loan-actions";

    // Renew button
    const renewButton = document.createElement("button");

    renewButton.type = "button";
    renewButton.className = "loan-renew-btn";
    renewButton.textContent = "Renew";

    renewButton.disabled = !canRenewLoan(loan);

    if (!canRenewLoan(loan)) {
      renewButton.title = getRenewalMessage(loan);
    }

    renewButton.addEventListener("click", () => {
      handleRenewLoan(loan.id, bookTitle, renewButton);
    });

    // Return button
    const returnButton = document.createElement("button");

    returnButton.type = "button";
    returnButton.className = "loan-return-btn";
    returnButton.textContent = "Return";

    returnButton.addEventListener("click", () => {
      handleReturnLoan(loan.id, bookTitle, returnButton);
    });


    //Create newwal eligibility message
    const renewalMessage = document.createElement("span");

    renewalMessage.className = "renewal-message";
    renewalMessage.textContent = getRenewalMessage(loan);

    //Apply a visual status
    if (getLoanDisplayStatus(loan) === "overdue") {
      renewalMessage.classList.add("renewal-overdue");
    } else if (canRenewLoan(loan)) {
      renewalMessage.classList.add("renewal-eligible");
    } else {
      renewalMessage.classList.add("renewal-unavailable");
    }

    actionWrapper.appendChild(renewButton);
    actionWrapper.appendChild(returnButton);
    actionWrapper.appendChild(renewalMessage);

    actionCell.appendChild(actionWrapper);
  });
}


async function handleReturnLoan(
  loanId,
  bookTitle,
  returnButton
) {
  const confirmed = window.confirm(
    `Are you sure you want to return "${bookTitle}"?`
  );

  if (!confirmed) return;

  returnButton.disabled = true;
  returnButton.textContent = "Returning...";

  try {
    const response = await fetch(
      `/api/v1/loans/${loanId}/return`,
      {
        method: "PATCH"
      }
    );

    const result = await response.json();

    if (!response.ok) {
      throw new Error(
        typeof result.detail === "string"
          ? result.detail
          : "Failed to return book"
      );
    }

    showLoanMessage(
      `Loan #${loanId} returned successfully!`
    );

    await Promise.all([
      loadActiveLoans(),
      loadLoanBooks(),
      loadBooks(),
      loadLoanHistory()
    ]);

  } catch (error) {
    console.error("Return failed:", error);
    showLoanMessage(error.message, true);

  } finally {
    returnButton.disabled = false;
    returnButton.textContent = "Return";
  }
}


async function loadLoanHistory() {
  const [loansResponse, membersResponse, booksResponse] =
    await Promise.all([
      fetch("/api/v1/loans"),
      fetch("/api/v1/members"),
      fetch("/api/v1/books")
    ]);

  if (
    !loansResponse.ok ||
    !membersResponse.ok ||
    !booksResponse.ok
  ) {
    throw new Error("Unable to load borrowing history");
  }

  const [loans, members, books] = await Promise.all([
    loansResponse.json(),
    membersResponse.json(),
    booksResponse.json()
  ]);

  const memberMap = new Map(
    members.map(member => [member.id, member.full_name])
  );

  const bookMap = new Map(
    books.map(book => [book.id, book.title])
  );

  allLoanHistory = loans.map(loan => ({
    ...loan,
    memberName:
      memberMap.get(loan.member_id) ?? `Member #${loan.member_id}`,
    bookTitle:
      bookMap.get(loan.book_id) ?? `Book #${loan.book_id}`
  }));

  filterLoanHistory();
}

function getLoanDisplayStatus(loan) {
  if (loan.status === "returned") {
    return "returned";
  }

  const dueValue = loan.due_at;

  const normalized =
    /(?:Z|[+-]\d{2}:\d{2})$/i.test(dueValue)
      ? dueValue
      : `${dueValue}Z`;

  const dueDate = new Date(normalized);

  if (
    loan.status === "borrowed" &&
    !Number.isNaN(dueDate.getTime()) &&
    dueDate < new Date()
  ) {
    return "overdue";
  }

  return "borrowed";
}


function renderLoanHistory(loans) {
  const tbody = document.getElementById("loan-history-body");

  if (!tbody) return;

  tbody.replaceChildren();

  if (loans.length === 0) {
    const row = tbody.insertRow();
    const cell = row.insertCell();

    cell.colSpan = 7;
    cell.textContent = "No matching loan records found.";
    return;
  }

  loans.forEach(loan => {
    const row = tbody.insertRow();

    const displayStatus = getLoanDisplayStatus(loan);

    const values = [
      loan.id,
      loan.memberName,
      loan.bookTitle,
      formatLoanDate(loan.borrowed_at),
      formatLoanDate(loan.due_at),
      loan.returned_at
        ? formatLoanDate(loan.returned_at)
        : "—",
        `${loan.renewal_count ?? 0} / ${MAX_LOAN_RENEWALS}`
    ];

    values.forEach(value => {
      const cell = row.insertCell();
      cell.textContent = String(value);
    });

    const statusCell = row.insertCell();

    const badge = document.createElement("span");
    badge.className = `loan-status ${displayStatus}`;
    badge.textContent =
      displayStatus.charAt(0).toUpperCase() +
      displayStatus.slice(1);

    statusCell.appendChild(badge);
  });
}

function filterLoanHistory() {
  const searchInput = document.getElementById("loan-search");
  const statusFilter = document.getElementById(
    "loan-status-filter"
  )

  if (!searchInput || !statusFilter) return;

  const searchText = searchInput.value.trim().toLowerCase();
  const selectedStatus = statusFilter.value;



  const filteredLoans = allLoanHistory.filter(loan => {
    const displayStatus = getLoanDisplayStatus(loan);

    const matchesSearch =
      loan.memberName.toLowerCase().includes(searchText) ||
      loan.bookTitle.toLowerCase().includes(searchText) ||
      String(loan.id).includes(searchText) ||
      String(loan.member_id).includes(searchText);


    const matchesStatus =
      selectedStatus === "all" ||
      displayStatus === selectedStatus;

    return matchesSearch && matchesStatus;
  });

  console.log("Filtering loans:", {
    searchText,
    selectedStatus,
    total: allLoanHistory.length,
    matched: filteredLoans.length
  });

  document.getElementById("loan-history-count").textContent =
    filteredLoans.length;

  renderLoanHistory(filteredLoans);

}

function initializeLoanHistory() {
  const searchInput = document.getElementById("loan-search");
  const statusFilter = document.getElementById(
    "loan-status-filter"
  );

  if (!searchInput || !statusFilter) {
    console.error("Loan history filter elements not found");
    return;
  }
  //Filter Whenever the user types
  searchInput.addEventListener("input", filterLoanHistory);

  //Filter whenever the selected status changes
  statusFilter.addEventListener("change", filterLoanHistory);

  console.log("Loan history filters initialized successfully");
}

function canRenewLoan(loan) {
  const displayStatus = getLoanDisplayStatus(loan);

  return (
    loan.status === "borrowed" &&
    displayStatus !== "overdue" &&
    (loan.renewal_count ?? 0) < MAX_LOAN_RENEWALS
  );
}

async function handleRenewLoan(
  loanId,
  bookTitle,
  renewButton
) {
  const confirmed = window.confirm(
    `Renew "${bookTitle}" for another loan period?`
  );

  if (!confirmed) return;

  renewButton.disabled = true;
  renewButton.textContent = "Renewing...";

  try {
    const response = await fetch(
      `/api/v1/loans/${loanId}/renew`,
      {
        method: "PATCH"
      }
    );

    const result = await response.json();

    if (!response.ok) {
      throw new Error(
        typeof result.detail === "string"
          ? result.detail
          : "Failed to renew loan"
      );
    }

    showLoanMessage(
      `Loan #${loanId} renewed successfully! ` +
      `New due date: ${formatLoanDate(result.due_at)}`
    );

    await Promise.all([
      loadActiveLoans(),
      loadLoanHistory()
    ]);

  } catch (error) {
    console.error("Loan renewal failed:", error);

    showLoanMessage(error.message, true);

    // Reload because the server may have newer policy or loan data.
    try {
      await Promise.all([
        loadActiveLoans(),
        loadLoanHistory()
      ]);
    } catch (refreshError) {
      console.error("Could not refresh loan data:", refreshError);
    }

  } finally {
    renewButton.disabled = false;
    renewButton.textContent = "Renew";
  }
}

function getRenewalMessage(loan) {
  const displayStatus = getLoanDisplayStatus(loan);

  if (loan.status === "returned") {
    return "Loan already returned"
  }

  if (displayStatus === "overdue") {
    return "Overdue - return required";
  }

  if ((loan.renewal_count ?? 0) >= MAX_LOAN_RENEWALS) {
    return "Renewal limit reached"
  }

  return "Eligible for renewal";

}


async function loadLibraryOverview() {
  const message = document.getElementById("analytics-message");
  const refreshButton = document.getElementById(
    "refresh-analytics-btn"
  );

  if (!message || !refreshButton) return;

  refreshButton.disabled = true;
  message.textContent = "Loading library analytics...";

  const metricElements = {
    total_book_titles: "metric-book-titles",
    total_book_copies: "metric-total-copies",
    available_book_copies: "metric-available-copies",
    borrowed_book_copies: "metric-borrowed-copies",
    active_members: "metric-active-members",
    overdue_loans: "metric-overdue-loans"
  };

  try {
    const response = await fetch("/api/v1/reports/overview");

    if (!response.ok) {
      throw new Error(
        `Failed to load reports (HTTP ${response.status})`
      );
    }

    const data = await response.json();

    Object.entries(metricElements).forEach(([field, elementId]) => {
      const element = document.getElementById(elementId);

      if (element) {
        element.textContent = String(data[field] ?? 0);
      }
    });

    message.textContent = "Analytics updated successfully.";

  } catch (error) {
    console.error("Library analytics error:", error);
    message.textContent = error.message;

  } finally {
    refreshButton.disabled = false;
  }
}


async function loadMostBorrowedBooks() {
  const container = document.getElementById(
    "most-borrowed-chart"
  );

  if (!container) return;

  container.textContent = "Loading popular books...";

  try {
    const response = await fetch(
      "/api/v1/reports/most-borrowed-books?limit=5"
    );

    if (!response.ok) {
      throw new Error("Unable to load popular books");
    }

    const books = await response.json();

    renderMostBorrowedBooks(books);

  } catch (error) {
    console.error("Most borrowed books error:", error);
    container.textContent = error.message;
  }
}


function renderMostBorrowedBooks(books) {
  const container = document.getElementById(
    "most-borrowed-chart"
  );

  container.replaceChildren();

  if (books.length === 0) {
    container.textContent = "No borrowing history yet.";
    return;
  }

  const maxCount = Math.max(
    ...books.map(book => book.borrow_count),
    1
  );

  books.forEach((book, index) => {
    const item = document.createElement("div");

    const label = document.createElement("div");
    label.className = "analytics-bar-label";

    const title = document.createElement("span");
    title.textContent = `${index + 1}. ${book.title}`;

    const count = document.createElement("strong");
    count.textContent = `${book.borrow_count} loans`;

    label.append(title, count);

    const track = document.createElement("div");
    track.className = "analytics-bar-track";

    const fill = document.createElement("div");
    fill.className = "analytics-bar-fill";

    fill.style.width = `${
      (book.borrow_count / maxCount) * 100
    }%`;

    track.appendChild(fill);
    item.append(label, track);
    container.appendChild(item);
  });
}


async function loadTopMembers() {
  const tbody = document.getElementById(
    "top-members-body"
  );

  if (!tbody) return;

  tbody.replaceChildren();

  const loadingRow = tbody.insertRow();
  const loadingCell = loadingRow.insertCell();

  loadingCell.colSpan = 5;
  loadingCell.textContent = "Loading top members...";

  try {
    const response = await fetch(
      "/api/v1/reports/top-members?limit=5"
    );

    if (!response.ok) {
      throw new Error(
        `Failed to load top members (HTTP ${response.status})`
      );
    }

    const members = await response.json();

    if (!Array.isArray(members)) {
      throw new Error("Invalid member analytics response");
    }

    renderTopMembers(members);

  } catch (error) {
    console.error("Top members report error:", error);

    tbody.replaceChildren();

    const row = tbody.insertRow();
    const cell = row.insertCell();

    cell.colSpan = 5;
    cell.textContent = "Unable to load member analytics.";
  }
}


function renderTopMembers(members) {
  const tbody = document.getElementById(
    "top-members-body"
  );

  if (!tbody) return;

  tbody.replaceChildren();

  // Handle members with no borrowing history.
  if (members.length === 0) {
    const row = tbody.insertRow();
    const cell = row.insertCell();

    cell.colSpan = 5;
    cell.textContent = "No member borrowing activity yet.";

    return;
  }

  members.forEach((member, index) => {
    const row = tbody.insertRow();

    const values = [
      index + 1,
      member.full_name,
      member.total_loans,
      member.active_loans,
      member.returned_loans
    ];

    values.forEach(value => {
      const cell = row.insertCell();
      cell.textContent = String(value);
    });

    //Highlight the top borrower.
    if (index ===  0 && member.total_loans > 0) {
      const memberCell = row.cells[1]


    const badge = document.createElement("span");

    badge.className = "top-borrower-badge";
    badge.textContent = "🏆 Top Borrower";

    memberCell.appendChild(badge);
    }
  });
}


async function loadOverdueLoans() {
  const tbody = document.getElementById(
    "overdue-loans-body"
  );

  const filter = document.getElementById(
    "overdue-min-days"
  );

  if (!tbody || !filter) return;

  tbody.replaceChildren();

  const loadingRow = tbody.insertRow();
  const loadingCell = loadingRow.insertCell();

  loadingCell.colSpan = 6;
  loadingCell.textContent = "Loading overdue loans...";

  const minDays = Number(filter.value);

  try {
    const response = await fetch(
      `/api/v1/reports/overdue-loans?min_days_overdue=${minDays}`
    );

    if (!response.ok) {
      throw new Error(
        `Failed to load overdue loans (HTTP ${response.status})`
      );
    }

    const loans = await response.json();

    if (!Array.isArray(loans)) {
      throw new Error("Invalid overdue report response");
    }

    renderOverdueLoans(loans);

  } catch (error) {
    console.error("Overdue analytics error:", error);

    tbody.replaceChildren();

    const row = tbody.insertRow();
    const cell = row.insertCell();

    cell.colSpan = 6;
    cell.textContent = "Unable to load overdue loans.";
  }
}


function renderOverdueLoans(loans) {
  const tbody = document.getElementById(
    "overdue-loans-body"
  );

  if (!tbody) return;

  tbody.replaceChildren();

  if (loans.length === 0) {
    const row = tbody.insertRow();
    const cell = row.insertCell();

    cell.colSpan = 6;
    cell.textContent = "No overdue loans found.";
    return;
  }

  loans.forEach(loan => {
    const row = tbody.insertRow();

    const values = [
      loan.loan_id,
      loan.member_name,
      loan.book_title,
      formatLoanDate(loan.due_at),
      loan.days_overdue
    ];

    values.forEach(value => {
      const cell = row.insertCell();
      cell.textContent = String(value);
    });

    // Display a visual priority indicator.
    const priorityCell = row.insertCell();

    const badge = document.createElement("span");

    badge.className =
      `overdue-priority overdue-priority--${loan.priority}`;

    badge.textContent =
      loan.priority.charAt(0).toUpperCase() +
      loan.priority.slice(1);

    priorityCell.appendChild(badge);
  });
}


function initializeAnalytics() {
  const refreshButton = document.getElementById(
    "refresh-analytics-btn"
  );

  const overdueFilter = document.getElementById(
    "overdue-min-days"
  );

  if (!refreshButton) {
    console.warn("Analytics refresh button not found");
    return;
  }

  async function refreshAllAnalytics() {
    await Promise.all([
      loadLibraryOverview(),
      loadMostBorrowedBooks(),
      loadTopMembers(),
      loadOverdueLoans()
    ]);
  }

  refreshButton.addEventListener(
    "click",
    refreshAllAnalytics
  );

  if (overdueFilter) {
    overdueFilter.addEventListener(
      "change",
      loadOverdueLoans
    );
  }

  // Initial dashboard load.
  refreshAllAnalytics();
}

// ===== APPLICATION INITIALIZATION =====

loadBooks();
loadMembers();
initializeLoanManagement();
initializeAnalytics();
