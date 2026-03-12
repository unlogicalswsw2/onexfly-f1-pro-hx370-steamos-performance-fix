# ⚡ OneXFly F1 Pro HX370 SteamOS Performance Fix

<p align="center">
  <img src="https://img.shields.io/badge/SteamOS-3.5%2B-blue?style=for-the-badge&logo=steam" alt="SteamOS">
  <img src="https://img.shields.io/badge/OneXFly-F1%20Pro-orange?style=for-the-badge" alt="OneXFly">
  <img src="https://img.shields.io/badge/CPU-HX%20370-green?style=for-the-badge" alt="HX370">
</p>

<p align="center">
  <a href="https://github.com/unlogicalswsw2/onexfly-f1-pro-hx370-steamos-performance-fix/stargazers">
    <img src="https://img.shields.io/github/stars/unlogicalswsw2/onexfly-f1-pro-hx370-steamos-performance-fix?style=for-the-badge&logo=github" alt="Stars">
  </a>
  <a href="https://github.com/unlogicalswsw2/onexfly-f1-pro-hx370-steamos-performance-fix/releases">
    <img src="https://img.shields.io/github/v/release/unlogicalswsw2/onexfly-f1-pro-hx370-steamos-performance-fix?style=for-the-badge&logo=git" alt="Release">
  </a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge&logo=opensourceinitiative" alt="License">
  </a>
</p>

<p align="center">
  <b>🚀 Decky Loader плагин, который исправляет критическое падение производительности на OneXFly F1 Pro (HX 370) при подключении к сети питания под SteamOS.</b>
</p>

---

## 📋 Содержание

- [Проблема](#-проблема)
- [Решение](#-решение)
- [Установка](#-установка)
- [Использование](#-использование)
- [Как это работает](#-как-это-работает)
- [Технические детали](#-технические-детали)
- [Системные требования](#-системные-требования)
- [Известные проблемы](#-известные-проблемы)
- [Часто задаваемые вопросы](#-часто-задаваемые-вопросы)
- [Для разработчиков](#-для-разработчиков)
- [Благодарности](#-благодарности)
- [Лицензия](#-лицензия)

---

## 🚨 Проблема

На **OneXFly F1 Pro** с процессором **AMD HX 370** под управлением **SteamOS** наблюдается странное поведение:

| Состояние | FPS | Поведение |
|-----------|-----|-----------|
| 🔋 **На батарее** | 60+ | ✅ Всё отлично, производительность высокая |
| 🔌 **При подключении питания** | 30-35 | ❌ Резкое падение производительности |

**Почему это происходит?**

Причина — конфликт между управлением питанием SteamOS и embedded-контроллером (EC) OneXFly. При подключении к сети система ошибочно занижает лимиты TDP и переводит ядра CPU в спящие состояния (C-States), вместо того чтобы повысить производительность.

---

## 💡 Решение

Плагин **принудительно** включает режимы максимальной производительности:

### ✅ Что делает фикс:

````bash
# 1. CPU — перевод всех ядер в режим performance
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# 2. GPU — ручное управление и профиль производительности
echo manual | sudo tee /sys/class/drm/card0/device/power_dpm_force_performance_level
echo 1 | sudo tee /sys/class/drm/card0/device/pp_power_profile_mode

# 3. Отключение конфликтующего сервиса
sudo systemctl disable power-profiles-daemon
```

### 📊 Результат:

| Метрика | До фикса | После фикса |
|---------|----------|-------------|
| FPS (под нагрузкой) | 30-35 | 55-60+ |
| Частота CPU (пиковая) | 1.8-2.5 GHz | 4.5-5.0 GHz |
| Частота GPU | ~1600 MHz | ~2000 MHz |
| Задержки (input lag) | Высокие | Низкие |

---

## 📥 Установка

### 🔧 Способ 1: Через магазин Decky (рекомендуется)

1. Убедитесь, что у вас установлен [Decky Loader](https://github.com/SteamDeckHomebrew/decky-loader)
2. Откройте **настройки Decky** (иконка шестеренки в панели плагинов)
3. Перейдите на вкладку **"Общие"**
4. В поле **"URL-адреса магазинов"** добавьте:

````bash
https://unlogicalswsw2.github.io/onexfly-f1-pro-hx370-steamos-performance-fix/
```

5. Нажмите **"Сохранить"**
6. Перейдите на вкладку **"Магазин"**
7. Найдите **"OneXFly F1 Pro HX370 SteamOS Performance Fix"**
8. Нажмите **"Установить"**

### 📦 Способ 2: Ручная установка

````bash
# Клонируйте репозиторий в папку плагинов Decky
cd ~/homebrew/plugins
git clone https://github.com/unlogicalswsw2/onexfly-f1-pro-hx370-steamos-performance-fix.git

# Установите зависимости и соберите
cd onexfly-f1-pro-hx370-steamos-performance-fix
pnpm install
pnpm run build

# Перезагрузите SteamOS или перезапустите Decky
```

### 💻 Способ 3: Прямая установка скрипта (без Decky)

Если вы не используете Decky Loader, можно установить только bash-скрипт:

````bash
curl -L https://raw.githubusercontent.com/unlogicalswsw2/onexfly-f1-pro-hx370-steamos-performance-fix/main/install.sh | bash
```

Или вручную:

````bash
# Скачайте скрипт
wget https://raw.githubusercontent.com/unlogicalswsw2/onexfly-f1-pro-hx370-steamos-performance-fix/main/fix-onexfly-performance.sh

# Сделайте исполняемым
chmod +x fix-onexfly-performance.sh

# Запустите
./fix-onexfly-performance.sh
```

---

## 🎮 Использование

После установки в панели Decky появится новая иконка **⚡**.

### Интерфейс плагина:

````bash
┌─────────────────────────────────┐
│  ⚡ OneXFly Performance Fix      │
├─────────────────────────────────┤
│                                  │
│  Статус: ████████░░ Включен      │
│                                  │
│  ┌─────────────────────────────┐ │
│  │ [⚡] Performance режим       │ │
│  │ └─────────────────────────┐ │ │
│  │   ON ●─────────────────○ OFF │ │
│  └─────────────────────────────┘ │
│                                  │
│  ⚠️ Включение может увеличить     │
│     энергопотребление в простое   │
└─────────────────────────────────┘
```

### 🔘 Элементы управления:

| Элемент | Действие |
|---------|----------|
| **Переключатель** | Вкл/Выкл фикс производительности |
| **Статус** | Отображает текущее состояние |
| **Кнопка "Установить"** | (если фикс не установлен) |

### ⏱️ Когда применяется фикс:

- **Мгновенно** — при переключении тумблера
- **Автоматически** — при каждой загрузке системы (если был включен)
- **После сна/гибернации** — автоматически восстанавливается

---

## 🔧 Как это работает

### Архитектура плагина

````bash
┌─────────────────────────────────────────────────────┐
│                    Decky Loader                      │
├─────────────────────────────────────────────────────┤
│  ┌──────────────┐          ┌──────────────────────┐ │
│  │  index.tsx   │◄────────►│      main.py         │ │
│  │  (Frontend)  │   JSON   │     (Backend)        │ │
│  └──────────────┘   RPC     └──────────┬───────────┘ │
│                                         ▼             │
│                              ┌──────────────────────┐ │
│                              │ Systemd Service      │ │
│                              │ onexfly-fix.service  │ │
│                              └──────────┬───────────┘ │
│                                         ▼             │
│                              ┌──────────────────────┐ │
│                              │  Bash Fix Script     │ │
│                              │  /usr/local/bin/     │ │
│                              └──────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

### Компоненты системы:

#### 1. **Bash-скрипт** (`/usr/local/bin/onexfly-performance-fix.sh`)

````bash
#!/bin/bash
# Принудительный performance режим для CPU
for g in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    echo performance > "$g"
done

# Принудительный performance режим для GPU
echo manual > /sys/class/drm/card0/device/power_dpm_force_performance_level
echo 1 > /sys/class/drm/card0/device/pp_power_profile_mode
```

#### 2. **Systemd сервис** (`/etc/systemd/system/onexfly-performance-fix.service`)

````bash
[Unit]
Description=OneXFly Performance Fix
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/onexfly-performance-fix.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

#### 3. **Python бэкенд** (`main.py` - упрощенно)

````bash
class Plugin:
    async def toggle_fix(self, enable: bool):
        if enable:
            subprocess.run(["systemctl", "start", "onexfly-performance-fix"])
        else:
            # Возврат к авто-режиму
            subprocess.run("echo auto > /sys/class/drm/card0/device/power_dpm_force_performance_level", shell=True)
```

---

## 📊 Технические детали

### Изменяемые параметры

| Параметр | Путь в sysfs | Значение по умолчанию | После фикса |
|----------|--------------|----------------------|-------------|
| CPU Governor | `/sys/devices/system/cpu/cpu*/cpufreq/scaling_governor` | `powersave` | `performance` |
| GPU Power Level | `/sys/class/drm/card0/device/power_dpm_force_performance_level` | `auto` | `manual` |
| GPU Profile | `/sys/class/drm/card0/device/pp_power_profile_mode` | `0` (auto) | `1` (performance) |
| power-profiles-daemon | systemd service | active | disabled |

### Мониторинг состояния

Проверьте, активен ли фикс:

````bash
# Проверка CPU
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor

# Проверка GPU
cat /sys/class/drm/card0/device/power_dpm_force_performance_level
cat /sys/class/drm/card0/device/pp_power_profile_mode
```

Ожидаемый вывод при включенном фиксе:

````bash
performance
manual
1
```

---

## 💻 Системные требования

### Минимальные:

| Компонент | Требование |
|-----------|------------|
| **Устройство** | OneXFly F1 Pro |
| **Процессор** | AMD HX 370 (или HX 365) |
| **ОС** | SteamOS 3.5+ (любая версия) |
| **Плагин** | Decky Loader v2.5+ |
| **Память** | 8 MB свободного места |

### Рекомендуемые:

| Компонент | Рекомендация |
|-----------|--------------|
| **BIOS** | v1.07e или новее |
| **SteamOS** | 3.9 или новее |
| **Блок питания** | 65W+ (GaN рекомендуется) |

---

## ⚠️ Известные проблемы

### 🟢 Решенные:

| Проблема | Статус | Решение |
|----------|--------|---------|
| Падение FPS при подключении питания | ✅ Fixed | Текущий плагин |
| Конфликт с power-profiles-daemon | ✅ Fixed | Сервис отключается |
| Группа dialout в SteamOS | ✅ Fixed | Используется `uucp` |

### 🟡 Текущие ограничения:

1. **Энергопотребление в простое**
   - При включенном фиксе CPU может потреблять на 2-3 Вт больше в простое
   - Рекомендуется выключать фикс, если не играете

2. **Температура**
   - Под нагрузкой температуры могут быть на 3-5°C выше
   - В пределах нормы для HX 370 (до 95°C)

3. **Совместимость**
   - Протестировано только на HX 370 и HX 365
   - На других процессорах может не работать

---

## ❓ Часто задаваемые вопросы

### Q: Безопасно ли это?
**A:** Да, полностью безопасно. Плагин только меняет программные параметры управления питанием, которые можно вернуть обратно выключением тумблера.

### Q: Нужно ли отключать перед сном?
**A:** Нет, плагин автоматически восстановит состояние после пробуждения.

### Q: Почему на батарее всё работает, а от сети нет?
**A:** Это баг во взаимодействии SteamOS и EC OneXFly. Система думает, что при подключении питания нужно экономить энергию (абсурд, но факт).

### Q: Поможет ли это на других играх?
**A:** Да, фикс влияет на систему в целом, поэтому все игры получат прирост.

### Q: Как удалить плагин?

````bash
# Через Decky: настройки → плагины → удалить

# Или вручную:
sudo systemctl disable onexfly-performance-fix.service
sudo rm /etc/systemd/system/onexfly-performance-fix.service
sudo rm /usr/local/bin/onexfly-performance-fix.sh
rm -rf ~/homebrew/plugins/onexfly-f1-pro-hx370-steamos-performance-fix
```

---

## 👨‍💻 Для разработчиков

### Локальная разработка на macOS

````bash
# Клонируйте репозиторий
git clone https://github.com/unlogicalswsw2/onexfly-f1-pro-hx370-steamos-performance-fix.git
cd onexfly-f1-pro-hx370-steamos-performance-fix

# Установите зависимости
pnpm install

# Режим разработки (следит за изменениями)
pnpm run watch

# Сборка
pnpm run build
```

### Структура проекта

````bash
onexfly-f1-pro-hx370-steamos-performance-fix/
├── 📁 src/
│   ├── 📄 index.tsx          # Фронтенд React
│   ├── 📄 styles.css          # Стили
│   └── 📄 types.ts            # TypeScript типы
├── 📁 bin/
│   └── 📄 main.py             # Бэкенд Python
├── 📄 package.json            # Зависимости
├── 📄 plugin.json             # Метаданные Decky
├── 📄 rollup.config.js        # Конфиг сборщика
├── 📄 fix-onexfly-performance.sh # Установочный скрипт
├── 📄 README.md                # Этот файл
└── 📄 LICENSE                  # MIT License
```

### API плагина

````bash
// Доступные методы для вызова из фронтенда
interface PluginAPI {
  // Включить/выключить фикс
  toggle_fix(enable: boolean): Promise<{success: boolean, message: string}>;
  
  // Получить текущий статус
  get_status(): Promise<{enabled: boolean}>;
  
  // Установить фикс в систему
  install_fix(): Promise<{success: boolean, message: string}>;
}
```

---

## 🙏 Благодарности

Особая благодарность:

- **Valve** — за SteamOS (несмотря на баги)

---

## 📄 Лицензия

MIT © [unlogicalswsw2](https://github.com/unlogicalswsw2)

````bash
Данное программное обеспечение предоставляется "как есть", 
без каких-либо гарантий. Вы можете использовать, модифицировать 
и распространять его в любых целях, включая коммерческие, 
с указанием оригинального авторства.
```

---

## ⭐ Поддержка проекта

Если плагин помог вам:

1. **Поставьте звезду** на GitHub — это мотивирует развивать проект
2. **Расскажите о проблеме** в сообществе — вдруг кто-то еще мучается
3. **Сообщите об ошибках** — создайте Issue в репозитории

---

<p align="center">
  <a href="https://github.com/unlogicalswsw2/onexfly-f1-pro-hx370-steamos-performance-fix">
    <img src="https://img.shields.io/github/stars/unlogicalswsw2/onexfly-f1-pro-hx370-steamos-performance-fix?style=social" alt="GitHub stars">
  </a>
  <br>
  <sub>Сделано с ❤️ для сообщества OneXFly</sub>
</p>
