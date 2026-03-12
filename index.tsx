import {
  PanelSection,
  PanelSectionRow,
  ToggleField,
  staticClasses,
  ButtonItem,
  DialogBody,
  DialogButton,
  DialogControlsSection,
  DialogHeader,
  showModal,
  ModalRoot
} from "@decky/ui";
import { definePlugin, routerHook } from "@decky/api";
import { useState, useEffect } from "react";
import { FaBolt } from "react-icons/fa";

// Компонент модального окна для подтверждения
const ConfirmModal = ({ closeModal, onConfirm, title, message }: {
  closeModal: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
}) => {
  return (
    <ModalRoot closeModal={closeModal}>
      <DialogHeader>{title}</DialogHeader>
      <DialogBody>
        <DialogControlsSection>
          <div style={{ padding: "10px", textAlign: "center" }}>
            {message}
          </div>
          <div style={{ display: "flex", gap: "10px", justifyContent: "center", marginTop: "20px" }}>
            <DialogButton onClick={closeModal}>Отмена</DialogButton>
            <DialogButton
              onClick={() => {
                onConfirm();
                closeModal();
              }}
              style={{ backgroundColor: "#e67e22" }}
            >
              Подтвердить
            </DialogButton>
          </div>
        </DialogControlsSection>
      </DialogBody>
    </ModalRoot>
  );
};

const Content = () => {
  const [enabled, setEnabled] = useState<boolean>(false);
  const [isInstalled, setIsInstalled] = useState<boolean>(true);
  const [loading, setLoading] = useState<boolean>(false);

  // Загружаем статус при монтировании
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const result = await DeckyPlugin.callServerMethod("get_status");
        setEnabled(result.enabled);
      } catch (error) {
        console.error("Failed to get status:", error);
      }
    };
    fetchStatus();
  }, []);

  const handleToggle = async (value: boolean) => {
    setLoading(true);
    try {
      const result = await DeckyPlugin.callServerMethod("toggle_fix", { enable: value });
      if (result.success) {
        setEnabled(value);
        // Показываем уведомление
        DeckyPlugin.toaster.toast({
          title: "OneXFly Performance Fix",
          body: result.message,
          duration: 3000
        });
      } else {
        DeckyPlugin.toaster.toast({
          title: "Ошибка",
          body: result.message,
          duration: 5000,
          critical: true
        });
      }
    } catch (error) {
      console.error("Toggle failed:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleInstall = () => {
    showModal(
      <ConfirmModal
        closeModal={() => {}}
        onConfirm={async () => {
          setLoading(true);
          try {
            const result = await DeckyPlugin.callServerMethod("install_fix");
            DeckyPlugin.toaster.toast({
              title: "OneXFly Performance Fix",
              body: result.message,
              duration: 3000
            });
            if (result.success) {
              setIsInstalled(true);
            }
          } catch (error) {
            console.error("Install failed:", error);
          } finally {
            setLoading(false);
          }
        }}
        title="Установка фикса"
        message="Это установит необходимые скрипты и сервис в систему. Продолжить?"
      />
    );
  };

  if (!isInstalled) {
    return (
      <PanelSection title="OneXFly Performance Fix">
        <PanelSectionRow>
          <div style={{ padding: "10px", textAlign: "center" }}>
            Фикс не установлен в системе
          </div>
        </PanelSectionRow>
        <PanelSectionRow>
          <ButtonItem
            layout="below"
            onClick={handleInstall}
            disabled={loading}
          >
            {loading ? "Установка..." : "Установить фикс"}
          </ButtonItem>
        </PanelSectionRow>
      </PanelSection>
    );
  }

  return (
    <PanelSection title="OneXFly Performance Fix">
      <PanelSectionRow>
        <div style={{ padding: "10px", backgroundColor: "#222", borderRadius: "8px", marginBottom: "10px" }}>
          <span style={{ color: enabled ? "#4caf50" : "#f44336", fontWeight: "bold" }}>
            Статус: {enabled ? "Включен" : "Выключен"}
          </span>
          <br />
          <small style={{ color: "#aaa" }}>
            Включение фиксирует CPU в режиме performance и GPU в manual режиме
          </small>
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <ToggleField
          label="Performance режим"
          description="Принудительно включить максимальную производительность"
          checked={enabled}
          onChange={handleToggle}
          disabled={loading}
          icon={<FaBolt />}
        />
      </PanelSectionRow>

      <PanelSectionRow>
        <div style={{ padding: "10px", fontSize: "12px", color: "#888" }}>
          <span>⚠️ Включение может увеличить энергопотребление</span>
        </div>
      </PanelSectionRow>
    </PanelSection>
  );
};

export default definePlugin(() => {
  return {
    name: "OneXFly Performance",
    titleView: <div style={{ display: "flex", gap: "10px" }}>OneXFly Performance</div>,
    content: <Content />,
    icon: <FaBolt />,
    onDismount() {
      console.log("Unloading OneXFly Performance Fix plugin");
    },
  };
});