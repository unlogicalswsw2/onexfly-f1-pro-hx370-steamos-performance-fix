import { callable, definePlugin, toaster } from "@decky/api";
import { ButtonItem, Field, PanelSection, PanelSectionRow, ToggleField } from "@decky/ui";
import { useCallback, useEffect, useState } from "react";
import { FaTachometerAlt } from "react-icons/fa";

type StatusResponse = {
  enabled: boolean;
};

const getStatus = callable<[], StatusResponse>("get_status");
const setEnabled = callable<[enabled: boolean], StatusResponse>("set_enabled");
const updatePlugin = callable<[], { ok: boolean; message: string }>("update_plugin");

function Content() {
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setError(null);
    try {
      setStatus(await getStatus());
    } catch (e) {
      setError(String(e));
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const onToggle = useCallback(
    async (enabled: boolean) => {
      setBusy(true);
      setError(null);
      try {
        setStatus(await setEnabled(enabled));
      } catch (e) {
        const msg = String(e);
        setError(msg);
        toaster.toast({
          title: "OneXFly Performance Fix",
          body: msg,
        });
        await refresh();
      } finally {
        setBusy(false);
      }
    },
    [refresh]
  );

  const onUpdate = useCallback(async () => {
    setUpdating(true);
    setError(null);
    try {
      const res = await updatePlugin();
      if (!res.ok) {
        setError(res.message);
        toaster.toast({
          title: "OneXFly Performance Fix",
          body: `Update failed: ${res.message}`,
        });
      } else {
        toaster.toast({
          title: "OneXFly Performance Fix",
          body: res.message,
        });
      }
    } catch (e) {
      const msg = String(e);
      setError(msg);
      toaster.toast({
        title: "OneXFly Performance Fix",
        body: `Update error: ${msg}`,
      });
    } finally {
      setUpdating(false);
    }
  }, []);

  const enabled = status?.enabled ?? false;

  return (
    <PanelSection title="OneXFly F1 Pro">
      <PanelSectionRow>
        <ToggleField
          label="Performance Fix"
          description={enabled ? "ON (performance mode applied)" : "OFF (defaults restored)"}
          checked={enabled}
          disabled={busy}
          onChange={onToggle}
        />
      </PanelSectionRow>

      <PanelSectionRow>
        <Field label="Status">{status === null ? "Loading…" : enabled ? "ON" : "OFF"}</Field>
      </PanelSectionRow>

      <PanelSectionRow>
        <ButtonItem disabled={updating} onClick={onUpdate}>
          {updating ? "Updating..." : "Update from GitHub"}
        </ButtonItem>
      </PanelSectionRow>

      {error && (
        <PanelSectionRow>
          <Field label="Error">{error}</Field>
        </PanelSectionRow>
      )}
    </PanelSection>
  );
}

export default definePlugin(() => {
  return {
    name: "OneXFly F1 Pro Performance Fix",
    titleView: <div />,
    content: <Content />,
    icon: <FaTachometerAlt />,
    onDismount() {},
  };
});

