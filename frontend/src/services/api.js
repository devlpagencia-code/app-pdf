const BACKEND_URL = "http://localhost:8000"

export async function sendEvents(events){
  return fetch(`${BACKEND_URL}/api/events`,{
    method:"POST",
    headers:{
      "Content-Type":"application/json"
    },
    body: JSON.stringify(events)
  })
}