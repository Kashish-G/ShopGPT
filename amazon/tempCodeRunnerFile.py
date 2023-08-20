if bank_offer_num_txt == 'offers':
                bank_offers =  soup_bank_offer.find_all('p', attrs={'class':'a-spacing-mini a-size-base-plus'})
                for offers in bank_offers:
                    print(offers.get_text())
            else:
                bank_offer = soup_bank_offer.find_all('h1', attrs={'class':'a-size-medium-plus a-spacing-medium a-spacing-top-small'})
                for offer in bank_offer:
                    offer_txt = offer.get_text()
                    offer_pure_txt = offer_txt.strip()
                    print(offer_pure_txt)
            print('------------------------------------')
            