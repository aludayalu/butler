const vscode = require("vscode");
const net = require("net");
const { exec } = require("child_process");
var port=0;

function isPortInUse(port) {
    return new Promise((resolve) => {
        const server = net.createServer();
        server.unref();

        server.on("error", () => {
            resolve(true);
        });

        server.listen(port, "127.0.0.1", () => {
            server.close();
            resolve(false);
        });
    });
}

async function findAvailablePort() {
    while (true) {
        const port = Math.floor(Math.random() * (50000 - 2000 + 1)) + 2000;
        const inUse = await isPortInUse(port);
        if (!inUse) {
            return port;
        }
    }
}

findAvailablePort().then((availablePort) => {
    exec("python3 main.py "+availablePort, {
		cwd: __dirname
	})
	port=availablePort
	console.log(availablePort)
});

function activate(context) {
	console.log("Your butler is now running!")

    let disposable = vscode.commands.registerCommand("butler.openSidePanel", function () {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            return;
        }

        const selection = editor.selection;
        const selectedText = editor.document.getText(selection);

        ButlerPanel.createOrShow(context, selectedText);
    });

    context.subscriptions.push(disposable);
}

function deactivate() {}

var panelInstance=null;

class ButlerPanel {
    static currentPanel = null;

    static createOrShow(context, selectedText) {
        if (ButlerPanel.currentPanel) {
            ButlerPanel.currentPanel._panel.reveal(vscode.ViewColumn.Two);
            ButlerPanel.currentPanel.update(selectedText);
            return;
        }

        const panel = vscode.window.createWebviewPanel(
            "butlerSidePanel",
            "Butler",
            { viewColumn: vscode.ViewColumn.Two, preserveFocus: false },
            { enableScripts: true }
        );

        ButlerPanel.currentPanel = new ButlerPanel(panel, context, selectedText);
    }

    constructor(panel, context, selectedText) {
        this._panel = panel;
        this._context = context;

        this._panel.onDidDispose(() => this.dispose(), null, context.subscriptions);

        this.update(selectedText);
    }

    update(selectedText) {
        this._panel.webview.html = this.getHtmlContent(selectedText);
    }

    dispose() {
        ButlerPanel.currentPanel = null;
        this._panel.dispose();
    }

    getHtmlContent(selectedText) {
        return `
<!DOCTYPE html>
<html lang="en">
<body>
    <div id="root">
        <h1>Your Butler is starting!</h1>
    </div>

    <script>
        var html="";
        const apiUrl = "http://127.0.0.1:${port}";

        setTimeout(async ()=>{
            while (true) {
                try {
                    var request=await fetch(apiUrl);
                    html=await request.text()
                    document.getElementById("root").innerHTML=html;
                    executeScripts(document.getElementById("root"));
                    break;
                } catch (e) {
                    console.log(e);
                    continue;
                }
            }
        }, 1000);

        function executeScripts(element) {
            element.querySelectorAll("script").forEach(script => {
                const newScript = document.createElement("script")
                if (script.src) {
                    newScript.src = script.src
                } else {
                    newScript.textContent = script.textContent
                }
                script.parentNode.replaceChild(newScript, script)
            })
        }
    </script>
</body>
</html>
`;
    }
}

module.exports = {
    activate,
    deactivate
};
