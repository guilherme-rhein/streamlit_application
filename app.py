import timeit
import pandas            as pd
import streamlit         as st
import seaborn           as sns
import matplotlib.pyplot as plt
from io import BytesIO
import os
from PIL import Image

# Função para converter o df para csv
@st.cache_data 
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

# Função para converter o df para excel
@st.cache_data 
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close()  # Fechar o escritor
    output.seek(0)
    return output
    

# Função para ler os dados
@st.cache_data 
def load_data(file_data):
     return pd.read_csv(file_data, sep=';')

# Função para filtrar baseado na multiseleção de categorias
@st.cache_data 
def multiselect_filter(relatorio, col, selecionados):
    if 'all' in selecionados:
        return relatorio
    else:
        return relatorio[relatorio[col].isin(selecionados)].reset_index(drop=True)


def main():
    file_path_icon = r"C:\Users\Guilherme Rhein\Downloads\git\streamlit_application\telmarketing_icon.png"
    st.set_page_config(page_title = 'Telemarketing analisys', 
        page_icon = Image.open(file_path_icon),
        layout="wide",
        initial_sidebar_state='expanded'
    )
    st.write('# Telemarketing analisys')
    st.markdown("---")
    
    file_path_bank = r"C:\Users\Guilherme Rhein\Downloads\git\streamlit_application\Bank-Branding.jpg"
    image = Image.open(file_path_bank)
    st.sidebar.image(image)


    st.sidebar.write("## Suba o arquivo")
    data_file_1 = st.sidebar.file_uploader("Bank marketing data", type=['csv','xlsx'])
    if (data_file_1 is not None):
        start = timeit.default_timer()
        bank_raw = load_data(data_file_1)
        bank = bank_raw.copy()
        st.write('## Antes dos filtros')
        st.write(bank_raw.head())
 


    #FORMS:
        with st.sidebar.form(key='my_form'):
        
            # IDADES
            max_age = int(bank.age.max())
            min_age = int(bank.age.min())
            idades = st.slider(label='Idade', 
                                min_value = min_age,
                                max_value = max_age, 
                                value = (min_age, max_age),
                                step = 1)


            # PROFISSÕES
            jobs_list = bank.job.unique().tolist()
            jobs_list.append('all')
            jobs_selected =  st.multiselect("Profissão", jobs_list, ['all'])

            # ESTADO CIVIL
            marital_list = bank.marital.unique().tolist()
            marital_list.append('all')
            marital_selected =  st.multiselect("Estado civil", marital_list, ['all'])

            # DEFAULT?
            default_list = bank.default.unique().tolist()
            default_list.append('all')
            default_selected =  st.multiselect("Default", default_list, ['all'])

            
            # TEM FINANCIAMENTO IMOBILIÁRIO?
            housing_list = bank.housing.unique().tolist()
            housing_list.append('all')
            housing_selected =  st.multiselect("Tem financiamento imob?", housing_list, ['all'])

            
            # TEM EMPRÉSTIMO?
            loan_list = bank.loan.unique().tolist()
            loan_list.append('all')
            loan_selected =  st.multiselect("Tem empréstimo?", loan_list, ['all'])

            
            # MEIO DE CONTATO?
            contact_list = bank.contact.unique().tolist()
            contact_list.append('all')
            contact_selected =  st.multiselect("Meio de contato", contact_list, ['all'])

            
            # MÊS DO CONTATO
            month_list = bank.month.unique().tolist()
            month_list.append('all')
            month_selected =  st.multiselect("Mês do contato", month_list, ['all'])

            
            # DIA DA SEMANA
            day_of_week_list = bank.day_of_week.unique().tolist()
            day_of_week_list.append('all')
            day_of_week_selected =  st.multiselect("Dia da semana", day_of_week_list, ['all'])


            bank = (bank.query("age >= @idades[0] and age <= @idades[1]")
                        .pipe(multiselect_filter, 'job', jobs_selected)
                        .pipe(multiselect_filter, 'marital', marital_selected)
                        .pipe(multiselect_filter, 'default', default_selected)
                        .pipe(multiselect_filter, 'housing', housing_selected)
                        .pipe(multiselect_filter, 'loan', loan_selected)
                        .pipe(multiselect_filter, 'contact', contact_selected)
                        .pipe(multiselect_filter, 'month', month_selected)
                        .pipe(multiselect_filter, 'day_of_week', day_of_week_selected)
            )

            submit_button = st.form_submit_button(label='Aplicar')

        st.write('## Após os filtros')
        st.write(bank.head())
        
        
        df_xlsx = to_excel(bank)
        st.download_button(label='📥 Download tabela: Dados filtrados em EXCEL',
                           data=df_xlsx ,
                           file_name= 'bank_filtered.xlsx',
                           mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        
        st.markdown("---")





        # # PLOTS    
    # Certifique-se de que as categorias 'yes' e 'no' estão presentes em ambos os conjuntos de dados
        categories = ['no', 'yes']
        bank_raw_target_perc = bank_raw.y.value_counts(normalize=True).reindex(categories, fill_value=0) * 100
        bank_target_perc = bank.y.value_counts(normalize=True).reindex(categories, fill_value=0) * 100

        fig, ax = plt.subplots(1, 2, figsize=(10, 5))

        # Dados brutos
        sns.barplot(x=bank_raw_target_perc.index,
                    y=bank_raw_target_perc.values,
                    ax=ax[0])

        for p in ax[0].patches:
            ax[0].annotate(f'{p.get_height():.2f}%',
                        (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center',
                        va='center',
                        xytext=(0, 10),
                        textcoords='offset points')

        ax[0].set_title('Dados brutos',
                        fontweight="bold")

        # Dados filtrados
        sns.barplot(x=bank_target_perc.index,
                    y=bank_target_perc.values,
                    ax=ax[1])

        for p in ax[1].patches:
            ax[1].annotate(f'{p.get_height():.2f}%',
                        (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center',
                        va='center',
                        xytext=(0, 10),
                        textcoords='offset points')

        ax[1].set_title('Dados filtrados',
                        fontweight="bold")

        # Exibir no Streamlit
        st.pyplot(fig)


        # Botões de download dos dados dos gráficos
        col1, col2 = st.columns(2)
        
        bank_raw_target_perc_ = bank_raw_target_perc.reset_index(drop=False)
        bank_target_perc_ = bank_target_perc.reset_index(drop=False)

        df_xlsx = to_excel(bank_raw_target_perc_)
        col1.write('### Proporção original')
        col1.write(bank_raw_target_perc_)
        col1.download_button(label='📥 Download',
                             data=df_xlsx ,
                             file_name= 'bank_original.xlsx')
            
        df_xlsx = to_excel(bank_target_perc_)
        col2.write('### Proporção filtrado')
        col2.write(bank_target_perc_)
        col2.download_button(label='📥 Download',
                             data=df_xlsx ,
                             file_name= 'bank_filtrado.xlsx')



if __name__ == '__main__':
	main()
    









