import { sendEvents } from "../services/api"

let queue = []

setInterval(()=>{

 if(queue.length === 0) return

 const events = [...queue]

 queue = []

 sendEvents(events)

},5000)

export function enqueueEvent(event){

 queue.push({ 
  ...event,
  timestamp:Date.now()
 })

}