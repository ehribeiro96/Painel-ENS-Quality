import { LoadingBlock } from "./StateBlocks";

export function RouteLoading() {
  return (
    <main className="screen-center" aria-busy="true" aria-live="polite">
      <LoadingBlock label="Carregando módulo..." />
    </main>
  );
}
