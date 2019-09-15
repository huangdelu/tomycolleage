function cve_malware() {
    var infoelement = document.getElementById("info").style.display="none";
}

function program() {
    var filter, table, tr, td, i;
    filter = "fa-times";
    table = document.getElementById("table");
    tr = table.getElementsByTagName("tr");
    for (i = 0; i < tr.length; i++) {
        td = tr[i].getElementsByTagName("td")[6];
        if (td) {
            if (td.innerHTML.indexOf(filter) > -1) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }
    }
}

function All() {
    var table, tr, i;
    table = document.getElementById("table");
    tr = table.getElementsByTagName("tr");
    for (i = 0; i < tr.length; i++) {
        tr[i].style.display = "";
    }
}

function Copy() {
    var copyText = document.getElementById("key");
    copyText.select();
    document.execCommand("copy");
    document.getSelection().removeAllRanges();
}

function Root() {
    document.getElementById('d').checked = false;
    document.getElementById('c').checked = false;
    document.getElementById('s').checked = false;
    document.getElementById('i').checked = false;
    document.getElementById('v').checked = false;
    document.getElementById('n').checked = false;
    document.getElementById('l').checked = false;
    document.getElementById('b').checked = false;
}

function NotRoot() {
    document.getElementById('r').checked = false;
}
