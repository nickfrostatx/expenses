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

window.onload = function() {
    var newPurchase = document.getElementById('new-purchase');
    var nameField = newPurchase.name;
    document.getElementById('plus').addEventListener('click', function() {
        newPurchase.classList.remove('hidden');
        nameField.focus();
    });
};
