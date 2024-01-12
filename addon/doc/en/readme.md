# UML: Universal Multilingual

## Overview

This add-on detects the language that NVDA is currently reading, and switches between different speech engines based on the detected language. Currently, it supports Japanese and non-Japanese identification only. We are willing to add detectable languages and improve the detection logic based on user contributions / suggestions.

## System requirements

Minimum supported NVDA version is 2021.1.

## Usage

1. Install this add-on.
2. Run the NVDA menu -> Universal Multilingual -> Settings of Universal Multilingual.
3. Select your primary language.
4. Select a switching strategy.
5. Set speech engines for each language.
6. Save settings.
7. Change synthesizer to Universal Multilingual from the NVDA speech settings.
8. Check "Automatic language switching" from the same dialog.

## Settings

Settings included in "Settings of Universal Multilingual" menu will be described below.

### Primary language

Set the language which is prioritized the most. Currently, it does not affect the behavior much.

### Switching strategy

Sentence: Checks the eintirety of the reading sentence. If it contains at least one Japanese character, it stops scanning and reads everything in Japanese. When Japanese is not included in the sentence, it reads using the non-Japanese speech engine.

Word: Checks the reading sentence character by character. Even if Japanese and non-Japanese are mixed, it reads the Japanese part using the Japanese speech engine, and reads non-Japanese part using the non-Japanese speech engine.

### Speech engines

Set speech engines which will be used as Japanese and non-Japanese speeches, respectively. The listview displays pairs of a language and a speech engine. Pressing "Select engine" allows you to change speech engine for the currently selected language.

Currently, it is not supported to use the same speech engine for different languages. For example, when you are using SAPI5 speech engine for non-Japanese, you cannot use SAPI5 for Japanese.

## Recommended settings

It is strongly recommended to check the "Trust voice's language when processing characters and symbols" checkbox, which is located under NVDA's speech settings. It is a bit hard to describe, but it results in better reading.

## Known issues and limitations

Some combinations of speech engines will not work properly. In most cases, it is due to the synthDriver's incorrect implementations, and it is not fixable no matter how Universal Multilingual tries its best. 

In order to change settings of each speech engine, you need to switch to the speech engine from NVDA's speech settings first, then modify to your preference there. Universal Multilingual is responsible only for switching speech engines, and does not support any features which hook into the behaviors of speech engines under its control.

Some events like cap pitch changing have not been supported yet. The support is planned in a near future.

It is possible to add supported languages in the future, but it only supports Japanese and non-Japanese detection at the moment since there's no developers who use other languages natively. If you want additional language support, please contact ACT Laboratory.

## Contacting

If you have a GitHub account, [Universal Multilingual's issues page](https://github.com/actlaboratory/UML/issues) is the fastest path to reach us.

For email support, please send an email to "support@actlab.org".

## Changelog

### 2024/01/13 Version 1.0.3

1. Supports NVDA 2024.1.

### 2023/03/21 Version 1.0.2

1. Supports NVDA 2023.1.

### 2022/10/20 Version 1.0.1

1. Fixed an issue where UML initialization was failing When UML was loaded on NVDA startup. This issue was causing side effects such as say all command failure or synth freezing followed by an infinite loop. 
