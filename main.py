import subprocess
import os
import time

class Plugin:
    async def _main(self):
        # Проверяем статус при запуске
        self.current_status = self.check_status()
        pass

    async def toggle_fix(self, enable: bool):
        """Включить/выключить фикс"""
        try:
            if enable:
                # Включаем фикс
                result = subprocess.run(
                    ["sudo", "/usr/local/bin/onexfly-performance-fix.sh"],
                    capture_output=True,
                    text=True
                )
                self.current_status = True
                return {"success": True, "message": "Фикс включен"}
            else:
                # Отключаем фикс (возвращаем авто-режим)
                # Для GPU
                subprocess.run(
                    "echo auto | sudo tee /sys/class/drm/card0/device/power_dpm_force_performance_level",
                    shell=True,
                    capture_output=True
                )
                # Для CPU
                subprocess.run(
                    "echo powersave | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor",
                    shell=True,
                    capture_output=True
                )
                # Отключаем сервис автозагрузки
                subprocess.run(["sudo", "systemctl", "disable", "onexfly-performance-fix.service"])
                self.current_status = False
                return {"success": True, "message": "Фикс выключен"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    async def get_status(self):
        """Проверить, включен ли фикс"""
        status = self.check_status()
        return {"enabled": status}

    def check_status(self):
        """Проверка текущего состояния"""
        try:
            # Проверяем GPU режим
            gpu_mode = subprocess.run(
                ["cat", "/sys/class/drm/card0/device/power_dpm_force_performance_level"],
                capture_output=True,
                text=True
            ).stdout.strip()
            
            # Проверяем CPU governor
            cpu_mode = subprocess.run(
                ["cat", "/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"],
                capture_output=True,
                text=True
            ).stdout.strip()
            
            # Считаем, что фикс включен если GPU в manual и CPU в performance
            return gpu_mode == "manual" and cpu_mode == "performance"
        except:
            return False

    async def install_fix(self):
        """Установить фикс в систему (если ещё не установлен)"""
        try:
            # Проверяем, существует ли скрипт
            if os.path.exists("/usr/local/bin/onexfly-performance-fix.sh"):
                return {"success": True, "message": "Фикс уже установлен"}
            
            # Создаем скрипт
            script_content = """#!/bin/bash

for g in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
do
    echo performance > $g
done

echo manual > /sys/class/drm/card0/device/power_dpm_force_performance_level
echo 1 > /sys/class/drm/card0/device/pp_power_profile_mode
"""
            # Записываем скрипт
            subprocess.run(
                f"echo '{script_content}' | sudo tee /usr/local/bin/onexfly-performance-fix.sh",
                shell=True
            )
            subprocess.run(["sudo", "chmod", "+x", "/usr/local/bin/onexfly-performance-fix.sh"])
            
            # Создаем systemd сервис
            service_content = """[Unit]
Description=OneXFly Performance Fix

[Service]
Type=oneshot
ExecStart=/usr/local/bin/onexfly-performance-fix.sh

[Install]
WantedBy=multi-user.target
"""
            subprocess.run(
                f"echo '{service_content}' | sudo tee /etc/systemd/system/onexfly-performance-fix.service",
                shell=True
            )
            subprocess.run(["sudo", "systemctl", "daemon-reload"])
            
            return {"success": True, "message": "Фикс успешно установлен"}
        except Exception as e:
            return {"success": False, "message": str(e)}