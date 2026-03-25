import { sendEvents } from "../services/api"

let queue = []


setInterval(() => {
    if (queue.length === 0) return;
    const events = [...queue];
    queue = [];
    console.log("[batchQueue] Enviando eventos:", events);
    sendEvents(events)
        .then(res => {
            console.log("[batchQueue] Resposta do backend:", res.status);
            if (!res.ok) {
                res.text().then(txt => console.error("[batchQueue] Erro backend:", txt));
            }
        })
        .catch(err => {
            console.error("[batchQueue] Falha ao enviar eventos:", err);
        });
}, 5000);

export function enqueueEvent(event){

 queue.push({ 
  ...event,
  timestamp:Date.now()
 })

}