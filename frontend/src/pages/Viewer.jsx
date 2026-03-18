import { useEffect, useState } from "react"
import PdfViewer from "../components/PdfViewer/PdfViewer"

function Viewer(){

 const [doc,setDoc] = useState(null)
 const [error,setError] = useState(null)
 const [loading,setLoading] = useState(true)

 useEffect(()=>{

  const params = new URLSearchParams(window.location.search)
  let docId = params.get("doc")
  if(!docId){
    const parts = window.location.pathname.split('/')
    if(parts.length > 1 && parts[1] === 'viewer' && parts[2]){
      docId = parts[2]
    }
  }

  if(!docId){
   setError("Documento não informado na URL (parâmetro 'doc' ou /viewer/<token>).")
   setLoading(false)
   return
  }

  fetch(`http://localhost:8000/api/document/${docId}`)
   .then(res=>{
    if(!res.ok){
     throw new Error(`Erro ${res.status}: ${res.statusText}`)
    }
    return res.json()
   })
   .then(data=>{
    setDoc(data)
   })
   .catch(e=>{
    setError(e.message)
   })
   .finally(()=>{
    setLoading(false)
   })

 },[])

 if(loading){

  return <div>Carregando documento...</div>

 }

 if(error){

  return <div style={{ padding: 20, color: "red" }}>Erro: {error}</div>

 }

 if(!doc){

  return <div>Documento não encontrado.</div>

 }

 return (

  <PdfViewer
   documentUrl={doc.url}
   documentId={doc.id}
  />

 )

}

export default Viewer