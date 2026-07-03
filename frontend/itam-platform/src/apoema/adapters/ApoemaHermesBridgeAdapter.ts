import { ApoemaChatBridgeAdapter, type ApoemaChatMessagePayload } from "./ApoemaChatBridgeAdapter";

export const ApoemaHermesBridgeAdapter = {
  health: ApoemaChatBridgeAdapter.health,
  listSessions: ApoemaChatBridgeAdapter.listSessions,
  createSession: ApoemaChatBridgeAdapter.createSession,
  renameSession: ApoemaChatBridgeAdapter.renameSession,
  deleteSession: ApoemaChatBridgeAdapter.deleteSession,
  listMessages: ApoemaChatBridgeAdapter.listMessages,
  sendMessage(token: string, sessionId: string, payload: ApoemaChatMessagePayload) {
    return ApoemaChatBridgeAdapter.sendMessage(token, sessionId, payload);
  },
};
