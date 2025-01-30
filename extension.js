const vscode = require("vscode");
const net = require("net");
const { exec } = require("child_process");
const path = require("path")
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

var activeEditor=null;

function activate(context) {
	console.log("Your butler is now running!")

    vscode.window.onDidChangeActiveTextEditor(editor => {
        if (editor) {
            activeEditor = editor;
        }
    });

    let disposable = vscode.commands.registerCommand("butler.openSidePanel", function () {
        const editor = vscode.window.activeTextEditor;
        activeEditor=editor;
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

        var extension=path.extname(vscode.window.activeTextEditor.document.uri.fsPath)

        this.update(selectedText, extension);

        this._panel.webview.onDidReceiveMessage(
            (message) => {
                switch (message.command) {
                    case "updateText":
                        ButlerPanel.replaceSelectedText(message.text);
                        break;
                }
            },
            null,
            context.subscriptions
        );
    }

    static replaceSelectedText(newText) {
        if (!activeEditor) {
            vscode.window.showErrorMessage("No active editor found.");
            return;
        }
    
        activeEditor.edit((editBuilder) => {
            editBuilder.replace(activeEditor.selection, newText);
        });
    }

    async update(selectedText, extension) {
        this._panel.webview.html = await this.getHtmlContent(selectedText, extension);
    }

    dispose() {
        ButlerPanel.currentPanel = null;
        this._panel.dispose();
    }

    async getHtmlContent(selectedText, extension) {
        while (true) {
            try {
                var url=`http://127.0.0.1:${port}`
                var request=await fetch(url);
                var html=await request.text()
                return html.replaceAll("{port}", String(port)).replaceAll("{selectedText}", selectedText.replace(/`/g, "\\`").replace(/\${/g, "\\${").replace(/}/g, "\\}")).replace("{extension}", extension.slice(1));
            } catch {
                continue
            }
        }
    }
}

module.exports = {
    activate,
    deactivate
};
