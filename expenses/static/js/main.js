var failMsg = 'Error communicating with the server.';

function request(method, url, data, success, error) {
    var xhr = new XMLHttpRequest();
    xhr.open(method, url);

    var body = undefined;
    if (data) {
        xhr.setRequestHeader('Content-Type', 'application/json');
        body = JSON.stringify(data);
    }

    xhr.onload = function() {
        var data;
        if (xhr.responseText) {
            // Parse the response, if it exists
            try {
                data = JSON.parse(xhr.responseText);
            } catch (e) {
                error(failMsg);
                return;
            }
        } else {
            // No data, for example a 204
            data = null;
        }

        if (xhr.status >= 200 && xhr.status < 400) {
            success(data);
            return;
        } else {
            error(data.msg || failMsg);
            return;
        }
    };

    xhr.onerror = function() {
        error(failMsg);
    };

    xhr.send(body);

    return xhr;
}

function createDiv(cls, text) {
    var div = document.createElement('div');
    div.className = cls;
    if (text !== undefined) {
        div.textContent = text;
    };
    return div;
}

var addExpense = (function() {
    var currentTable = null;
    var lastExpenseDate = null;

    return function(expense, container) {
        if (expense.date != lastExpenseDate) {
            lastExpenseDate = expense.date;
            container.appendChild(createDiv('date', expense.date));
            currentTable = createDiv('box table');
            container.appendChild(currentTable);
        };

        var row = createDiv('row');
        row.appendChild(createDiv('cell user', expense.user));
        row.appendChild(createDiv('cell name', expense.name));
        row.appendChild(createDiv('cell price', expense.price));
        currentTable.appendChild(row);
    };
})();

window.onload = function() {
    var plus = document.getElementById('plus');
    if (plus) {
        var newPurchase = document.getElementById('new-purchase');
        var nameField = newPurchase.name;
        plus.addEventListener('click', function() {
            newPurchase.classList.remove('hidden');
            nameField.focus();
        });
    };

    var addExpenses = (function() {
        var container = document.getElementsByClassName('container')[0];
        return function(data) {
            for (var i = 0; i < data.expenses.length; i++) {
                addExpense(data.expenses[i], container);
            };
        };
    })();

    addExpenses(data);

    var loadMsg = document.getElementById('loading');
    var loadMoreExpenses = (function() {
        // This closure locks when called, and releases on a successful response
        // If the response has an error, the lock is never released
        var next = data.links.next;
        var loading = false;

        return function() {
            if (!loading) {
                if (next) {
                    loading = true;
                    request('GET', next, null, function(d) {
                        loading = false;
                        addExpenses(d);
                        next = d.links.next;
                        onScroll();
                    }, function(msg) {
                        loadMsg.textContent = 'Error loading more expenses';
                        console.error(msg);
                    });
                } else {
                    loadMsg.textContent = '';
                    loading = true;
                };
            };
        };
    })();

    function onScroll() {
        var toBottom = document.body.offsetHeight - window.pageYOffset
            - window.innerHeight;
        if (toBottom < 200) {
            loadMoreExpenses();
        };
    };

    window.addEventListener('scroll', onScroll);
    onScroll();

    if (data.expenses.length == 0) {
        loadMsg.textContent = 'No transactions have been added yet!';
    };
};
