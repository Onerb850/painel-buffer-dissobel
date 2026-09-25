import pandas as pd
import json
import os
import datetime

def parse_num(val):
    if pd.isna(val): return 0.0
    val_str = str(val).replace('.', '').replace(',', '.')
    try: return float(val_str)
    except: return 0.0

def run_process(base_dir='.'):
    buf_candidates = [os.path.join(base_dir, 'BUFFER.csv'), 'BUFFER.csv']
    buf_file = next((f for f in buf_candidates if os.path.exists(f)), 'BUFFER.csv')
    df = pd.read_csv(buf_file, sep=';', encoding='utf-8-sig')

    # Regra oficial de Atendimento (alinhada à Mesa Operacional / Cora):
    # Soma de todos os itens com situação de atendimento Atendido e Atendido Parcial (volume efetivamente faturado),
    # em todas as situações operacionais ativas (Registrado, Aguardando roteirização, Bloqueado, Aguardando vínculo,
    # Ordem de Carga, Carregado, Saída CDD, etc.), excluindo estritamente pedidos cancelados (CANCELADO) e itens anulados (ANULADO).
    df_atendido = df[
        (df['Situação atend. pedido'].isin(['ATENDIDO', 'ATENDIDO_PARCIAL'])) &
        (df['Situação pedido'] != 'CANCELADO')
    ].copy()

    df_atendido['quant_num'] = df_atendido['Quant. venda'].apply(parse_num)
    df_atendido['hl_num'] = df_atendido['Volume hectolitro'].apply(parse_num)
    df_atendido['cod_prod'] = pd.to_numeric(df_atendido['Cód. produto'], errors='coerce')

    # Base Completa de Produtos (01.11.csv / 03.01.11.csv)
    prod_candidates = [
        os.path.join(base_dir, '01.11.csv'),
        os.path.join(base_dir, '03.01.11.csv'),
        '01.11.csv',
        '03.01.11.csv'
    ]
    prod_file = next((f for f in prod_candidates if os.path.exists(f)), '01.11.csv')
    df_prod = pd.read_csv(prod_file, sep=';', encoding='latin1', usecols=[0, 12, 21])
    col_code = df_prod.columns[0]
    col_peso = df_prod.columns[1]
    col_pallet = df_prod.columns[2]

    df_prod_clean = pd.DataFrame({
        'cod_prod': pd.to_numeric(df_prod[col_code], errors='coerce'),
        'peso_unit_kg': df_prod[col_peso].apply(parse_num),
        'cx_pallet': df_prod[col_pallet].apply(parse_num)
    }).dropna(subset=['cod_prod']).drop_duplicates(subset=['cod_prod'])

    df_atendido = df_atendido.merge(df_prod_clean, on='cod_prod', how='left')
    df_atendido['peso_unit_kg'] = df_atendido['peso_unit_kg'].fillna(0.0)
    df_atendido['cx_pallet'] = df_atendido['cx_pallet'].fillna(0.0)

    # Cálculo do peso total e paletes por linha
    df_atendido['peso_total_kg'] = df_atendido['quant_num'] * df_atendido['peso_unit_kg']
    df_atendido['pallet_total'] = df_atendido.apply(
        lambda r: (r['quant_num'] / r['cx_pallet']) if r['cx_pallet'] > 0 else 0.0,
        axis=1
    )

    total_pedidos = int(df_atendido['Número pedido'].nunique())
    total_clientes = int(df_atendido['Cód. cliente'].nunique())
    total_produtos = int(df_atendido['Cód. produto'].nunique())
    total_cidades = int(df_atendido['Desc. município'].nunique())
    total_volume_hl = round(float(df_atendido['hl_num'].sum()), 2)
    total_quantidade = round(float(df_atendido['quant_num'].sum()), 0)
    total_peso_kg = round(float(df_atendido['peso_total_kg'].sum()), 2)
    total_peso_ton = round(float(total_peso_kg / 1000.0), 2)
    total_pallets = round(float(df_atendido['pallet_total'].sum()), 2)

    # Daily
    daily_df = df_atendido.groupby('Data entrega').agg(
        pedidos=('Número pedido', 'nunique'),
        volume_hl=('hl_num', 'sum'),
        quantidade=('quant_num', 'sum'),
        peso_kg=('peso_total_kg', 'sum'),
        pallets=('pallet_total', 'sum')
    ).reset_index()

    daily_data = []
    for _, row in daily_df.iterrows():
        daily_data.append({
            'data': str(row['Data entrega']),
            'pedidos': int(row['pedidos']),
            'volume_hl': round(float(row['volume_hl']), 2),
            'quantidade': round(float(row['quantidade']), 0),
            'peso_kg': round(float(row['peso_kg']), 2),
            'pallets': round(float(row['pallets']), 2)
        })

    # Ranking Produtos
    prod_rank = df_atendido.groupby(['Cód. produto', 'Desc. produto']).agg(
        quantidade=('quant_num', 'sum'),
        volume_hl=('hl_num', 'sum'),
        peso_kg=('peso_total_kg', 'sum'),
        pallets=('pallet_total', 'sum'),
        peso_unit_kg=('peso_unit_kg', 'first'),
        cx_pallet=('cx_pallet', 'first')
    ).reset_index().sort_values(by='volume_hl', ascending=False)

    products_data = []
    for _, row in prod_rank.iterrows():
        products_data.append({
            'cod': int(row['Cód. produto']),
            'produto': str(row['Desc. produto']),
            'quantidade': int(round(float(row['quantidade']))),
            'hl': round(float(row['volume_hl']), 2),
            'peso_kg': round(float(row['peso_kg']), 2),
            'pallets': round(float(row['pallets']), 2),
            'peso_unit_kg': round(float(row['peso_unit_kg']), 3),
            'cx_pallet': int(round(float(row['cx_pallet'])))
        })

    # Ranking Clientes
    client_rank = df_atendido.groupby(['Cód. cliente', 'Nome cliente', 'Nome fantasia', 'Desc. município']).agg(
        pedidos=('Número pedido', 'nunique'),
        quantidade=('quant_num', 'sum'),
        volume_hl=('hl_num', 'sum'),
        peso_kg=('peso_total_kg', 'sum'),
        pallets=('pallet_total', 'sum')
    ).reset_index().sort_values(by='volume_hl', ascending=False)

    clients_data = []
    for _, row in client_rank.iterrows():
        fantasia = str(row['Nome fantasia']).strip()
        nome = str(row['Nome cliente']).strip()
        exibicao = fantasia if fantasia and fantasia.lower() != 'nan' else nome
        subtitulo = nome if exibicao != nome else ''
        
        clients_data.append({
            'cod': int(row['Cód. cliente']),
            'nome': exibicao,
            'razao': subtitulo,
            'cidade': str(row['Desc. município']),
            'pedidos': int(row['pedidos']),
            'quantidade': int(round(float(row['quantidade']))),
            'hl': round(float(row['volume_hl']), 2),
            'peso_kg': round(float(row['peso_kg']), 2),
            'pallets': round(float(row['pallets']), 2)
        })

    # Ranking Cidades
    city_rank = df_atendido.groupby('Desc. município').agg(
        pedidos=('Número pedido', 'nunique'),
        clientes=('Cód. cliente', 'nunique'),
        quantidade=('quant_num', 'sum'),
        volume_hl=('hl_num', 'sum'),
        peso_kg=('peso_total_kg', 'sum'),
        pallets=('pallet_total', 'sum')
    ).reset_index().sort_values(by='volume_hl', ascending=False)

    cities_data = []
    for _, row in city_rank.iterrows():
        cities_data.append({
            'cidade': str(row['Desc. município']),
            'pedidos': int(row['pedidos']),
            'clientes': int(row['clientes']),
            'quantidade': int(round(float(row['quantidade']))),
            'hl': round(float(row['volume_hl']), 2),
            'peso_kg': round(float(row['peso_kg']), 2),
            'pallets': round(float(row['pallets']), 2)
        })

    # Base Integral para a aba "Análise por Cliente" (inclui Venda, Bonificação, Troca e Remessa)
    df['cod_prod'] = pd.to_numeric(df['Cód. produto'], errors='coerce')
    df['quant_num'] = df['Quant. venda'].apply(parse_num)
    df['hl_num'] = df['Volume hectolitro'].apply(parse_num)

    df_all_merged = df.merge(df_prod_clean, on='cod_prod', how='left')
    df_all_merged['peso_unit_kg'] = df_all_merged['peso_unit_kg'].fillna(0.0)
    df_all_merged['cx_pallet'] = df_all_merged['cx_pallet'].fillna(0.0)
    df_all_merged['peso_total_kg'] = df_all_merged['quant_num'] * df_all_merged['peso_unit_kg']
    df_all_merged['pallet_total'] = df_all_merged.apply(
        lambda r: (r['quant_num'] / r['cx_pallet']) if r['cx_pallet'] > 0 else 0.0,
        axis=1
    )

    clients_lookup = {}
    for cod_cliente, group in df_all_merged.groupby('Cód. cliente'):
        fantasia = str(group['Nome fantasia'].iloc[0]).strip()
        nome = str(group['Nome cliente'].iloc[0]).strip()
        cidade = str(group['Desc. município'].iloc[0]).strip()
        exibicao = fantasia if fantasia and fantasia.lower() != 'nan' else nome
        razao = nome if exibicao != nome else ''
        
        # Linhas ativas (não canceladas/anuladas) para consolidação de carga
        active_mask = (group['Situação pedido'] != 'CANCELADO') & (group['Situação atend. pedido'] != 'ANULADO')
        active_group = group[active_mask]
        
        tot_pedidos = int(active_group['Número pedido'].nunique())
        tot_hl = round(float(active_group['hl_num'].sum()), 2)
        tot_peso = round(float(active_group['peso_total_kg'].sum()), 2)
        tot_pallets = round(float(active_group['pallet_total'].sum()), 2)
        tot_qtd = int(round(float(active_group['quant_num'].sum())))
        
        # Tabela de produtos comprados pelo cliente (linhas ativas)
        prods = []
        for (cp, dp), pgroup in active_group.groupby(['Cód. produto', 'Desc. produto']):
            prods.append({
                'cod': int(cp),
                'produto': str(dp),
                'quantidade': int(round(float(pgroup['quant_num'].sum()))),
                'hl': round(float(pgroup['hl_num'].sum()), 2),
                'peso_kg': round(float(pgroup['peso_total_kg'].sum()), 2),
                'pallets': round(float(pgroup['pallet_total'].sum()), 2)
            })
        prods.sort(key=lambda x: x['hl'], reverse=True)
        
        # Tabela de pedidos individuais do cliente
        orders = []
        for num_ped, ogroup in group.groupby('Número pedido'):
            is_canc = bool((ogroup['Situação pedido'] == 'CANCELADO').any() or (ogroup['Situação atend. pedido'] == 'ANULADO').any())
            orders.append({
                'numero_pedido': str(num_ped),
                'data_entrega': str(ogroup['Data entrega'].iloc[0]),
                'situacao_pedido': str(ogroup['Situação pedido'].iloc[0]),
                'situacao_atend': str(ogroup['Situação atend. pedido'].iloc[0]),
                'tipo_movimento': str(ogroup['Desc. tipo movimento'].iloc[0]),
                'operacao': str(ogroup['Desc. operação'].iloc[0]),
                'hl': round(float(ogroup['hl_num'].sum()), 2),
                'peso_kg': round(float(ogroup['peso_total_kg'].sum()), 2),
                'pallets': round(float(ogroup['pallet_total'].sum()), 2),
                'quantidade': int(round(float(ogroup['quant_num'].sum()))),
                'is_cancelled': is_canc
            })
        orders.sort(key=lambda x: (x['is_cancelled'], -x['hl']))
        
        clients_lookup[str(int(cod_cliente))] = {
            'cod': int(cod_cliente),
            'nome': exibicao,
            'razao': razao,
            'cidade': cidade,
            'total_pedidos': tot_pedidos,
            'total_hl': tot_hl,
            'total_peso_kg': tot_peso,
            'total_pallets': tot_pallets,
            'total_quantidade': tot_qtd,
            'total_itens_distintos': len(prods),
            'produtos': prods,
            'pedidos': orders
        }

        # Data de entrega e data de atualização dinâmicas (horário oficial de Brasília UTC-3)
    datas_entrega = [str(d).strip() for d in df_atendido['Data entrega'].dropna().unique() if str(d).strip()]
    data_entrega_str = ' / '.join(sorted(datas_entrega)) if datas_entrega else 'Não informada'
    tz_brasilia = datetime.timezone(datetime.timedelta(hours=-3))
    ultima_atualizacao_str = datetime.datetime.now(tz_brasilia).strftime('%d/%m/%Y %H:%M:%S')

    data = {
        'summary': {
            'total_volume_hl': total_volume_hl,
            'total_pedidos': total_pedidos,
            'total_clientes': total_clientes,
            'total_produtos': total_produtos,
            'total_cidades': total_cidades,
            'total_quantidade': int(total_quantidade),
            'total_linhas': len(df_atendido),
            'total_peso_kg': total_peso_kg,
            'total_peso_ton': total_peso_ton,
            'total_pallets': total_pallets,
            'data_entrega': data_entrega_str,
            'ultima_atualizacao': ultima_atualizacao_str
        },
        'daily': daily_data,
        'products': products_data,
        'clients': clients_data,
        'cities': cities_data,
        'clients_lookup': clients_lookup
    }

    json_path = os.path.join(base_dir, 'data.json')
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        pass

    sync_path = os.path.join(base_dir, 'last_sync.json')
    try:
        with open(sync_path, 'w', encoding='utf-8') as f:
            json.dump({
                'success': True,
                'timestamp': ultima_atualizacao_str,
                'data_entrega': data_entrega_str,
                'summary': data['summary'],
                'files': ['BUFFER.csv', '01.11.csv']
            }, f, ensure_ascii=False, indent=2)
    except Exception as e:
        pass

    print(f"data.json successfully updated! HL: {total_volume_hl} | Pedidos: {total_pedidos} | Clientes: {total_clientes} | Peso: {total_peso_kg:,.2f} kg ({total_peso_ton} ton) | Pallets: {total_pallets:,.2f}")
    return data

if __name__ == '__main__':
    run_process()

