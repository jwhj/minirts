let port = Number(new URLSearchParams(location.search).get('port'))
console.log(port)
function passInstruction() {
    let el = document.querySelector('#user-input-inst')
    let inst = el.value
    el.value = ''
    fetch(`/pass_inst`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            port: port,
            inst: inst
        })
    });
}
function sendEmptyInst() {
    fetch(`/pass_inst`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            port: port,
            inst: 'null'
        })
    });
}
function sendHeartbeat(port) {
    console.log(new Date());
    fetch(`/heartbeat/${port}`).then(() => {
        setTimeout(() => { sendHeartbeat(port) }, 2000);
    }).catch(console.log);
}
function inst_input_init() {
    document.querySelector('#user-input-inst').addEventListener('keydown', ev => {
        if (ev.key == 'Enter') {
            passInstruction();
            ev.preventDefault();
        }
    });
    $('#select-inst li').on('click', function () {
        let el = document.querySelector('#user-input-inst')
        el.value = $(this).text().split(' | ')[0].trimEnd();
        el.focus();
    });
    sendHeartbeat(port);
    addEventListener('beforeunload', (e) => {
        // e.preventDefault();
        fetch(`/stop_game/${port}`)
    }, {
        capture: true
    });
    console.log('test');
}