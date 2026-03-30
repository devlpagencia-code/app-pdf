import { useEffect, useRef } from "react";
import { tracker } from "../../analytics/tracker.js";
import * as pdfjsLib from "pdfjs-dist/build/pdf";

pdfjsLib.GlobalWorkerOptions.workerSrc = "/node_modules/pdfjs-dist/build/pdf.worker.min.mjs";

function PdfViewer({ documentUrl, documentId }) {
  const containerRef = useRef(null);
  const observerRef = useRef(null);

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
      }, { threshold: 0.6 });

      pages.forEach(p => observer.observe(p));

      observerRef.current = observer;
    }

    // 👇 função única correta
    const handleUnload = () => {
      tracker.endSession();
    };

    window.addEventListener("beforeunload", handleUnload);

    load();

    return () => {
      window.removeEventListener("beforeunload", handleUnload);

      // 👇 limpa observer
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };

  }, [documentUrl]);

  return (
    <div
      style={{
        height: "100vh",
        overflowY: "scroll",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: "24px",
        padding: "20px"
      }}
      ref={containerRef}
    />
  );
}

export default PdfViewer;