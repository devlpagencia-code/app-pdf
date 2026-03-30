import { enqueueEvent } from "./batchQueue"

class Tracker {
  constructor() {
    this.session = null
    this.currentPage = null
    this.pageStart = null
    this.documentId = null
    this.closed = false
    this.started = false
  }

  startSession(documentId) {
    this.started = true
    this.documentId = documentId
    this.session = crypto.randomUUID()

    // 👇 salva no navegador
    localStorage.setItem("tracker_session", this.session)
    localStorage.setItem("tracker_document", documentId)

    enqueueEvent({
      event_type: "document_open",
      session_id: this.session,
      document_id: documentId,
      timestamp: Date.now(),
      page: null
    })
  }

  pageView(page) {
    const now = Date.now()

    if (this.currentPage) {
      enqueueEvent({
        event_type: "page_time",
        session_id: this.session,
        document_id: this.documentId,
        page: this.currentPage,
        timestamp: now,
        metadata: {
          duration_ms: now - this.pageStart
        }
      })
    }

    this.currentPage = page
    this.pageStart = now

    enqueueEvent({
      event_type: "page_view",
      session_id: this.session,
      document_id: this.documentId,
      page,
      timestamp: now
    })
  }

  endSession() {
    if (this.closed) return
    this.closed = true

    const session = this.session || localStorage.getItem("tracker_session")
    const documentId = this.documentId || localStorage.getItem("tracker_document")

    if (!session || !documentId) {
      console.warn("document_close ignorado (sem sessão válida)")
      return
    }

    const now = Date.now()
    const events = []

    // 👇 salva tempo da última página
    if (this.currentPage && this.pageStart) {
      events.push({
        event_type: "page_time",
        session_id: session,
        document_id: documentId,
        page: this.currentPage,
        timestamp: now,
        metadata: {
          duration_ms: now - this.pageStart
        }
      })
    }

    // 👇 document close
    events.push({
      event_type: "document_close",
      session_id: session,
      document_id: documentId,
      timestamp: now,
      page: null
    })

    navigator.sendBeacon(
      "/api/events",
      JSON.stringify(events)
    )
  }
}

export const tracker = new Tracker()