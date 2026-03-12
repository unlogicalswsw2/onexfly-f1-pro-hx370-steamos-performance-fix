import { callable, definePlugin } from "@decky/api";
import { Field, PanelSection, PanelSectionRow, ToggleField } from "@decky/ui";
import { useCallback, useEffect, useState } from "react";
import { FaTachometerAlt } from "react-icons/fa";

type StatusResponse = {
  enabled: boolean;
  device_ok: boolean;
  device_name: string | null;
};

const getStatus = callable<[], StatusResponse>("get_status");
const setEnabled = callable<[enabled: boolean], StatusResponse>("set_enabled");

function Content() {
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [busy, setBusy] = useState(false);
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
        setError(String(e));
        await refresh();
      } finally {
        setBusy(false);
      }
    },
    [refresh]
  );

  const enabled = status?.enabled ?? false;

  return (
    <PanelSection title="OneXFly F1 Pro">
      <PanelSectionRow>
        <ToggleField
          label="Performance Fix"
          description={enabled ? "ON (performance mode applied)" : "OFF (defaults restored)"}
          checked={enabled}
          disabled={busy || (status !== null && !status.device_ok)}
          onChange={onToggle}
        />
      </PanelSectionRow>

      <PanelSectionRow>
        <Field label="Device">
          {status === null ? "Loading…" : status.device_name ?? "Unknown"}
        </Field>
      </PanelSectionRow>

      {status !== null && !status.device_ok && (
        <PanelSectionRow>
          <Field label="Status">Unsupported device (intended for OneXFly F1 Pro)</Field>
        </PanelSectionRow>
      )}

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

