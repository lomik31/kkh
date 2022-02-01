
import http from "https";
var privateKey = fs.readFileSync('ssl/lomik31.codead.dev.pem').toString();
var certificate = fs.readFileSync('ssl/lomik31.codead.dev.key').toString();
const credentials = {
    key: privateKey, 
    cert: certificate
};
import cors from "cors";
import fs from "fs";
function readFile() {
    var content = fs.readFileSync('../logs/logs.log', 'utf8');
    return content
}

var server = http.createServer(credentials, (req, res) => {
    //if (req. == "file") res.status(200).send(readFile());
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
server.listen(3000);