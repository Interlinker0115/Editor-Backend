from bs4 import BeautifulSoup, NavigableString
import csv
import urllib.parse
import re

def html_control(html_path):
    with open(html_path, 'r', encoding='UTF-8') as file:
        htmlString = file.read()

    # Parsing the HTML string
    soup = BeautifulSoup(htmlString, 'html.parser')

    try:
        # Standardization of table and image name
        for text_element in soup.find_all(text=True):
            updated_text = text_element
            if 'cuadro' in text_element.lower():
                updated_text = updated_text.replace('Cuadro', 'Tabla').replace('cuadro', 'Tabla')
            if 'imagen' in text_element.lower():
                updated_text = updated_text.replace('Imagen', 'Figura').replace('imagen', 'Figura')
            text_element.replace_with(updated_text)

        # Finding and removing the <style> tag from <head>
        style_tag = soup.head.find('style')
        if style_tag:
            style_tag.decompose()
        
        
        ## Replace formula to editable mathml formula
        # read .formula.csv file and then make mathml formula list
        mathmls = []
        mathml_path = html_path.replace('.html', '.formula.csv')

        with open(mathml_path, newline='', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                cleaned_mathml = row[0].replace('block', '')
                mathmls.append(cleaned_mathml)

        # Find all <span> elements with class "math-block"
        # math_block_spans = soup.find_all('span', class_='math-block')
        try:
            math_block_spans = soup.find_all(
                lambda tag: tag.name == 'span' and ('math-block' in tag.get('class', []) or 'math-inline' in tag.get('class', []))
            )
            # Extract <svg> elements within the math-block spans
            math_index = 0
            for span in math_block_spans:
                svg_elements = span.find_all('svg')
                for svg in svg_elements:
                    # Parse the MathML string into a BeautifulSoup object
                    mathml_soup = BeautifulSoup(mathmls[math_index], 'html.parser')
                    svg.replace_with(mathml_soup)
                    math_index += 1
        except Exception as e:
            print('you are right')
            print(e)
                
        ## svg font control according to the position
        # Find all <span> tags with class is "math-inline"
        math_inline_spans = soup.find_all('span', class_='math-inline')
        for span in math_inline_spans:
            span_parent = span.parent
            if span_parent.name == 'th':
                all_svg = span.find_all('svg')
                for svg in all_svg:
                    svg['style'] = 'color: white; font-size: 12px;'
            elif span_parent.name == 'td':
                all_svg = span.find_all('svg')
                for svg in all_svg:
                    svg['style'] = 'font-size: 12px'
            else :
                all_svg = span.find_all('svg')
                for svg in all_svg:
                    svg['style'] = 'font-size: 15px'


        #First Resumen exception handling and bold of Palabras clave:
        for h1 in soup.find_all('h1'):
            if h1.text.strip().lower() == 'resumen':
                print('oh you are right')
                new_h2_tag = soup.new_tag('h2')
                new_h2_tag.string = "RESUMEN"
                h1.replace_with(new_h2_tag)
        for div in soup.find_all('div'):
            if div.text.strip().startswith('Resumen'):
                text_content = div.text
                first_word, remaining_text = text_content.split(' ', 1)
                # Create a new <h2> tag for the first word
                new_h2_tag = soup.new_tag('h2')
                new_h2_tag.string = first_word
                
                # Create a new <div> tag for the remaining text
                new_div_tag = soup.new_tag('div')
                new_div_tag.string = remaining_text
                
                # replace the div tag to new h2 tag and div tag
                div.replace_with(new_h2_tag)
                new_h2_tag.insert_after(new_div_tag)
            if div.text.strip().lower().startswith('palabras clave:'):
                text_content = div.text
                first_word, remaining_text = text_content.split(':', 1)
                # Create a new <div> tag for the first word
                div_tag = soup.new_tag("div")
                new_palabras_tag = soup.new_tag('span')
                new_palabras_tag.string = first_word + ":"
                new_palabras_tag['style'] = "font-weight: bold"
                
                # Create a new <div> tag for the remaining text
                new_span_tag = soup.new_tag('span')
                new_span_tag.string = remaining_text
                
                div_tag.append(new_palabras_tag)
                div_tag.append(new_span_tag)
                
                div.replace_with(div_tag)

        # Finding and removing all content before the first h2 heading tag
        preview_content_div = soup.find('div', id='preview-content')

        if preview_content_div:
            # Finding the first <h2> tag within the target div
            first_h2 = preview_content_div.find('h2')
            
            if first_h2:
                # Finding all elements before the first <h2> tag
                for element in list(preview_content_div.children):
                    if element == first_h2:
                        break  # Stop when the first <h2> is reached
                    if isinstance(element, NavigableString):
                        continue  # Skip navigable strings (like whitespace)
                    element.decompose()  # Remove the element

        #keyword check
        # Keywords to check in the content of <h2> tags
        keywords = ["RESUMEN", "Introducción", "Metodología", "Resultados", "Conclusiones", "CONCLUSIÓN", "Agradecimientos", "Referencias", "CONCLUSIONES Y DISCUSIÓN", "ANEXOS", "BIBLIOGRAFÍA", "REFERENCIAS BIBLIOGRÁFICAS"]

        # Find all <h2> tags
        h2_tags = soup.find_all('h2')

        for h2 in h2_tags:
            # Check if the content of the <h2> tag matches any of the keywords
            if any(keyword.lower() in h2.text.lower() for keyword in keywords):
                # Create a new <h3> tag with the same content and attributes as the <h2> tag
                new_h2 = soup.new_tag('h2')
                new_h2.attrs = h2.attrs
                if h2.string is not None:
                    new_h2.string = h2.string.upper()
                else:
                    # If h2.string is None, you might want to assign an empty string,
                    # use h2.text, or handle the situation in another way.
                    new_h2.string = h2.text  # or some other handling
                
                # Replace the <h2> tag with the new <new_h2> tag
                h2.replace_with(new_h2)
            else:
                # Create a new <h3> tag with the same content and attributes as the <h2> tag
                h3 = soup.new_tag('h3')
                h3.attrs = h2.attrs
                if h2.string is not None:
                    h3.string = h2.string
                else:
                    # If h2.string is None, you might want to assign an empty string,
                    # use h2.text, or handle the situation in another way.
                    h3.string = h2.text  # or some other handling
                
                # Replace the <h2> tag with the new <h3> tag
                h2.replace_with(h3)

        # Make the section tag
        h2_tags = soup.find_all('h2')
        sections = []

        for h2_tag in h2_tags:
            # Create section tag
            section = soup.new_tag('section')
            
            # Move the <h2> and subsequent elements to the next <h2> into the section
            current_element = h2_tag
            while current_element:
                next_element = current_element.next_sibling
                if next_element and next_element.name == 'h2':
                    # Stop if the next <h2> tag is reached
                    break
                # Move the current element into the section
                section.append(current_element.extract())
                current_element = next_element
            
            sections.append(section)

        # Insert sections back into the document
        for section in sections:
            preview_content_div.append(section)

        # Add style to new html doc
        link_tag = soup.new_tag("link", href="https://fonts.googleapis.com/css2?family=Open+Sans&display=swap", rel="stylesheet")
        soup.head.append(link_tag)
        style_tag = soup.new_tag('style')
        style_tag.string="""
            body {
                    padding: 0;
                    margin: 0;
                    color: #606c71;
                    font-family: "Open Sans", "Helvetica Neue", Helvetica, Arial, sans-serif;
                }

            #container-ruller {
                width: 100vw;
                height: 48px;
                background-image: linear-gradient(120deg, rgb(21, 87, 153), rgb(21, 153, 87)) !important;
            }

            #preview-content {
                margin: 0 auto;
                padding: 2rem 4rem;
                max-width: 70rem;
            }

            h2 {
                color: rgb(21, 153, 87);
                font-family: "Open Sans", "Helvetica Neue", Helvetica, Arial, sans-serif;
                font-size: 1.5rem;
                font-weight: 400;
                margin: 0 0 16px 0;
                padding-top: 20px;
            }
            
            div {
                padding: 10px;
            }
            
            p {
                border: 0 !important;
                margin: 0 !important;
            }
            
            section div, span, 
            li {
                margin: 15.6px 0;
                color: rgb(96, 108, 113);
                font-size: 1.1rem;
                line-height: 26.4px;
                text-align: justify;
                font-weight: 200;
                font-family: "Open Sans", "Helvetica Neue", Helvetica, Arial, sans-serif;
            }

            .math-block {
                display: flex;
                justify-content: center;
            }

            img {
                width: 80%;
                height: auto;
            }

            .Wirisformula {
                width: auto!important;
                height: auto;
                margin: auto;
            }

            table {
                display: table;
                border-color: gray;
                border-collapse: collapse;
                border-spacing: 0;
                word-break: keep-all;
                font-size: 0.8em;
            }

            tr {
                display: table-row;
            }

            th {
                display: table-cell;
                font-weight: 700;
                background-color: #159957 !important;
                color: white;
                padding: 0.5rem 1rem;
                border-bottom: 1px solid #e9ebec;
                text-align: left;
            }

            td {
                padding: .5rem 1rem;
                border-bottom: 1px solid #e9ebec;
                text-align: left;
            }

            tbody {
                display: table-row-group;
                vertical-align: middle;
                unicode-bidi: isolate;
                border-color: inherit;
            }
            table tr:nth-child(odd) {
                background-color: #f2f2f2;
            }
            a {
                color: #1e6bb8;
                text-decoration: none;
            }
            td svg {
                height: 0.8rem;
            }

            blockquote {
                border-left: 5px solid #ccc;
                margin-bottom: 1em;
                margin-left: 20px;
                margin-right: 0;
                padding-left: 1.5em;
                padding-right: 1.5em;
            }

            figure {
                margin: 0;
            }
        """
        soup.head.append(style_tag)
        
        # Add style for figure and base content
        div_tags = preview_content_div.find_all('div')
        li_tags = preview_content_div.find_all('li')

        for li in li_tags:
            # Check if the content of the <div> tag includes both "Figure" and ":"
            if li.text and ("figura" in li.text.lower() and ":" in li.text or "gráfico" in li.text.lower() and ":" in li.text or "cuadro" in li.text.lower() and ":" in li.text):
                # Add an inline style attribute to the <li> tag
                li['style'] = 'text-align: center; margin: 0;'
            if "fuente:" in li.text.lower() or "euente:" in li.text.lower() or "nota." in li.text.lower():
                li['style'] = 'font-size: 0.9rem; text-align: justify; display: block; padding: 0; margin: 0px !important;'
                
        for div in div_tags:
            # Check if the content of the <div> tag includes both "Figure" and ":"
            if div.text and ("figura" in div.text.lower() and ":" in div.text or "gráfico" in div.text.lower() and ":" in div.text or "cuadro" in div.text.lower() and ":" in div.text or "tabla" in div.text.lower() and ":" in div.text):
                # Add an inline style attribute to the <div> tag
                div['style'] = 'text-align: center; margin: 0;'
            if "fuente:" in div.text.lower() or "euente:" in div.text.lower() or "nota." in div.text.lower():
                div['style'] = 'font-size: 0.9rem; text-align: justify; display: block; padding: 0; margin: 0px !important;'
        
        ## Eliminate the footnotes
        # Remove <hr> tags
        for hr_tag in soup.find_all('hr'):
            hr_tag.decompose()

        # Remove tags with class name 'footnotes'
        for footnotes_tag in soup.find_all(class_='footnotes'):
            footnotes_tag.decompose()
    except Exception as e:
        print('error occured')
        print(e)
        
    # Serializing back to HTML string
    modifiedHtmlString = str(soup)

    try:
        # Step 1: Replace 'Cuadro' with 'Tabla' and 'Imagen' with 'Figura'
        for text_node in soup.find_all(text=True):
            if 'Cuadro' in text_node or 'Imagen' in text_node:
                updated_text = text_node.replace('Cuadro', 'Tabla').replace('Imagen', 'Figura')
                text_node.replace_with(updated_text)

        # Function to wrap references in bold tags
        def wrap_references_in_bold(text):
            # Regular expression to find "Tabla" or "Figura" followed by a number
            pattern = re.compile(r'(Tabla|Figura) \d+')
            # Replace matches with bold tags
            return pattern.sub(lambda match: f'<b>{match.group(0)}</b>', text)

        # Step 2: Iterate through all text nodes again to wrap references in bold
        for text_node in soup.find_all(text=True):
            updated_text = wrap_references_in_bold(text_node)
            # Replace the text node with the new HTML content
            new_soup = BeautifulSoup(updated_text, 'html.parser')
            text_node.replace_with(new_soup)
    except Exception as e:
        print('yes')
        print(e)

    with open(html_path.replace('.html', '.convert.html'), 'w', encoding='UTF-8') as file:
        file.write(modifiedHtmlString)

    return html_path.replace('.html', '.convert.html')
