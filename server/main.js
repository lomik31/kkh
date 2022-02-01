import express from "express";
import https from "https";
import fs from "fs";
import ocsp from "ocsp/lib/ocsp.js";
const app = express();
const port = 3000;
const ocspCache = new ocsp.Cache();
const options = { //подключение сертификата и приватного ключа для него
        key: fs.readFileSync('/home/sun/ssl/lomik31.codead.dev.key'),
        cert: fs.readFileSync('/home/sun/ssl/lomik31.codead.dev.pem'),
    };
const httpsServer = https.createServer(options,app); //ставим сервер
httpsServer.listen(port); //слушаем порт ${port}

httpsServer.on('OCSPRequest', function(cert, issuer, callback) { //какаято хуета не разобрался сам
    ocsp.getOCSPURI(cert, function(err, uri) {
        if (err) return callback(error);
        var req = ocsp.request.generate(cert, issuer);
        var options = {
            url: uri,
            ocsp: req.data
        };
        ocspCache.request(req.id, options, callback);
    });
});
console.log(`Вроде запустился на порту ${port}`);
function readFile() {
    var content = fs.readFileSync('../logs/logs.log', 'utf8');
    return content
}
app.get("/", (req, res) => {
    switch (req.query.action) {
        case "readFile":
            res.status(200).send(readFile());
            break;
        case "getInfo":
            if (!req.query.id) break;
            console.log(req.query);
            let usrs = JSON.parse(fs.readFileSync('../usrs.json', 'utf8'));
            if (usrs.users[req.query.id] != undefined) res.status(200).json(JSON.stringify(usrs.users[req.query.id], null, "\n"));
            else res.status(200).json({"error":"user is not found"});
        default:
            break;
    }
})