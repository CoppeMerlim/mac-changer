import subprocess
import re
import sys
import time
from typing import Optional, Tuple

def get_network_adapters() -> list:
    """Obtém a lista de adaptadores de rede disponíveis."""
    try:
        output = subprocess.check_output("netsh interface show interface", shell=True).decode()
        adapters = []
        for line in output.split('\n'):
            if line.strip() and not line.startswith('Admin State'):
                parts = line.strip().split()
                if len(parts) >= 2:
                    name = ' '.join(parts[1:])
                    adapters.append(name)
        return adapters
    except subprocess.CalledProcessError:
        print("Erro ao obter adaptadores de rede.")
        return []

def get_current_mac(adapter_name: str) -> Optional[str]:
    """Obtém o MAC address atual do adaptador especificado."""
    try:
        output = subprocess.check_output(f"getmac /v /fo csv | findstr /i \"{adapter_name}\"", shell=True).decode()
        mac = re.search(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', output)
        return mac.group(0) if mac else None
    except subprocess.CalledProcessError:
        return None

def change_mac_address(adapter_name: str, new_mac: str) -> bool:
    """Altera o MAC address do adaptador especificado."""
    try:
        # Desabilita o adaptador
        subprocess.run(f"netsh interface set interface \"{adapter_name}\" admin=disable", shell=True)
        time.sleep(2)
        
        # Altera o MAC address
        subprocess.run(f"reg add \"HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Class\\{{4d36e972-e325-11ce-bfc1-08002be10318}}\\0001\" /v NetworkAddress /t REG_SZ /d {new_mac.replace(':', '')} /f", shell=True)
        
        # Reabilita o adaptador
        subprocess.run(f"netsh interface set interface \"{adapter_name}\" admin=enable", shell=True)
        return True
    except subprocess.CalledProcessError:
        return False

def generate_random_mac() -> str:
    """Gera um MAC address aleatório."""
    import random
    mac = [random.randint(0x00, 0xff) for _ in range(6)]
    return ':'.join([f"{x:02x}" for x in mac])

def main():
    while True:
        print("\n=== Gerenciador de MAC Address ===")
        print("1. Listar adaptadores de rede")
        print("2. Mostrar MAC address atual")
        print("3. Alterar MAC address")
        print("4. Restaurar MAC address original")
        print("5. Sair")
        
        choice = input("\nEscolha uma opção (1-5): ")
        
        if choice == "1":
            adapters = get_network_adapters()
            print("\nAdaptadores de rede disponíveis:")
            for i, adapter in enumerate(adapters, 1):
                print(f"{i}. {adapter}")
                
        elif choice == "2":
            adapters = get_network_adapters()
            if not adapters:
                print("Nenhum adaptador encontrado.")
                continue
                
            print("\nAdaptadores disponíveis:")
            for i, adapter in enumerate(adapters, 1):
                print(f"{i}. {adapter}")
                
            try:
                adapter_choice = int(input("\nEscolha o número do adaptador: ")) - 1
                if 0 <= adapter_choice < len(adapters):
                    mac = get_current_mac(adapters[adapter_choice])
                    if mac:
                        print(f"\nMAC address atual: {mac}")
                    else:
                        print("Não foi possível obter o MAC address.")
                else:
                    print("Opção inválida.")
            except ValueError:
                print("Por favor, insira um número válido.")
                
        elif choice == "3":
            adapters = get_network_adapters()
            if not adapters:
                print("Nenhum adaptador encontrado.")
                continue
                
            print("\nAdaptadores disponíveis:")
            for i, adapter in enumerate(adapters, 1):
                print(f"{i}. {adapter}")
                
            try:
                adapter_choice = int(input("\nEscolha o número do adaptador: ")) - 1
                if 0 <= adapter_choice < len(adapters):
                    new_mac = generate_random_mac()
                    print(f"\nNovo MAC address gerado: {new_mac}")
                    confirm = input("Deseja aplicar este MAC address? (s/n): ")
                    
                    if confirm.lower() == 's':
                        if change_mac_address(adapters[adapter_choice], new_mac):
                            print("MAC address alterado com sucesso!")
                        else:
                            print("Erro ao alterar o MAC address.")
                    else:
                        print("Operação cancelada.")
                else:
                    print("Opção inválida.")
            except ValueError:
                print("Por favor, insira um número válido.")
                
        elif choice == "4":
            adapters = get_network_adapters()
            if not adapters:
                print("Nenhum adaptador encontrado.")
                continue
                
            print("\nAdaptadores disponíveis:")
            for i, adapter in enumerate(adapters, 1):
                print(f"{i}. {adapter}")
                
            try:
                adapter_choice = int(input("\nEscolha o número do adaptador: ")) - 1
                if 0 <= adapter_choice < len(adapters):
                    if change_mac_address(adapters[adapter_choice], "000000000000"):
                        print("MAC address restaurado com sucesso!")
                    else:
                        print("Erro ao restaurar o MAC address.")
                else:
                    print("Opção inválida.")
            except ValueError:
                print("Por favor, insira um número válido.")
                
        elif choice == "5":
            print("Encerrando o programa...")
            sys.exit(0)
            
        else:
            print("Opção inválida. Por favor, escolha uma opção entre 1 e 5.")

if __name__ == "__main__":
    main() 