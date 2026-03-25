import { useEffect, useRef } from "react";
import { tracker } from "../../analytics/tracker.js";

import * as pdfjsLib from "pdfjs-dist/build/pdf";
// Definir o caminho do worker do PDF.js
pdfjsLib.GlobalWorkerOptions.workerSrc = "/node_modules/pdfjs-dist/build/pdf.worker.min.mjs";

function PdfViewer({ documentUrl, documentId }) { 
  const containerRef = useRef(null);

  useEffect(() => {
    let pdfDoc;

    async function load() {
      try {
        const task = pdfjsLib.getDocument({ url: documentUrl });
        pdfDoc = await task.promise;
        tracker.startSession(documentId);
        await renderPages(pdfDoc);
        setupTracking();
      } catch (err) {
        console.error("Falha ao carregar PDF:", err);
        const container = containerRef.current;
        if (container) {
          container.innerHTML = `<div style=\"color:red;padding:20px;\">Erro ao carregar PDF: ${err.message || "Documento inválido"}</div>`;
        }
      }
    }

    async function renderPages(pdf) {
      const container = containerRef.current;
      for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);
        const viewport = page.getViewport({ scale: 1.4 });
        const canvas = document.createElement("canvas");
        canvas.dataset.page = i;
        const ctx = canvas.getContext("2d");
        canvas.width = viewport.width;
        canvas.height = viewport.height;
        container.appendChild(canvas);
        await page.render({
          canvasContext: ctx,
          viewport
        }).promise;
      }
    }

    function setupTracking() {
      const pages = document.querySelectorAll("canvas[data-page]");
      const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const page = Number(entry.target.dataset.page);
            tracker.pageView(page);
          }
        });
      }, {
        threshold: 0.6
      });
      pages.forEach(p => observer.observe(p));
    }

    // Função para enviar document_close
    function sendDocumentClose() {
      if (tracker.session && documentId) {
        const event = {
          event_type: "document_close",
          session_id: tracker.session,
          document_id: documentId,
          timestamp: Date.now(),
          page: null
        };
        const url = "http://localhost:8000/api/events";
        const blob = new Blob([JSON.stringify([event])], { type: "application/json" });
        navigator.sendBeacon(url, blob);
      }
      tracker.endSession();
    }

    // Listener para fechar aba
    window.addEventListener("beforeunload", sendDocumentClose);

    load();

    return () => {
      window.removeEventListener("beforeunload", sendDocumentClose);
      sendDocumentClose(); // também chama no unmount
    };

  }, [documentUrl]);

 return (

  <div
   
   style={{
    height:"100vh",
    overflowY:"scroll",
    display:"flex",
    flexDirection:"column",
    alignItems:"center",
    gap:"24px",
    padding:"20px"
  }}
  ref={containerRef}>
  </div>
 )
}

export default PdfViewer