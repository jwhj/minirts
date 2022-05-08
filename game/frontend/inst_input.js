let port = Number(new URLSearchParams(location.href).get('port'))
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
function inst_input_init() {
    document.querySelector('#user-input-inst').addEventListener('keydown', ev => {
        if (ev.key == 'Enter') {
            passInstruction();
            ev.preventDefault();
        }
    });
    $('#select-inst li').on('click', function () {
        let el = document.querySelector('#user-input-inst')
        el.value = $(this).text();
        el.focus();
    });
    addEventListener('beforeunload', (e) => {
        e.preventDefault();
        fetch(`/stop_game/${port}`)
        return e.returnValue = 'test';
    }, {
        capture: true
    });
    console.log('test');
}