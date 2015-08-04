var current = 'O';
function cross() {
    if (this.innerHTML !== '') {
        // Has clicked before.
        return;
    }
    this.innerHTML = current;
    if (current === 'O') {
        current = 'X';
    } else {
        current = 'O';
    }
}

var cells = document.getElementsByClassName('cell');
for (var i = 0; i < cells.length; i++) {
    cells[i].onclick = cross;
}
