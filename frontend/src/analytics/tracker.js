import { enqueueEvent } from "./batchQueue"

class Tracker {
  constructor() {
    this.session = null
    this.currentPage = null
    this.pageStart = null
    this.documentId = null
  }

  startSession(documentId) {
    this.documentId = documentId
    this.session = crypto.randomUUID()

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
        timestamp: now
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
    if (this.currentPage) {
      enqueueEvent({
        event_type: "page_time",
        session_id: this.session,
        document_id: this.documentId,
        page: this.currentPage,
        timestamp: Date.now()
      })
    }

    enqueueEvent({
      event_type: "document_close",
      session_id: this.session,
      document_id: this.documentId,
      timestamp: Date.now(),
      page: null
    })
  }
}

export const tracker = new Tracker()