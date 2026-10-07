
import "@testing-library/jest-dom";
import { render, screen } from "@testing-library/react";
import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import { MemoryRouter } from "react-router-dom";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";

import { BaseWrapper } from "src/utils/Wrapper";

import enCommon from "../../../public/i18n/locales/en/common.json";
import zhTWCommon from "../../../public/i18n/locales/zh-TW/common.json";
import { Nav } from "./Nav";

vi.mock("openapi/queries", () => ({
vi.mock("./PluginMenus", () => ({ PluginMenus: () => <div /> }));
vi.mock("./TimezoneModal", () => ({ default: () => <div /> }));

beforeAll(async () => {
  await i18n.use(initReactI18next).init({
    defaultNS: "common",
    fallbackLng: "en",
    interpolation: { escapeValue: false },
    lng: "en",
    resources: {
      en: { common: enCommon },
      "zh-TW": { common: zhTWCommon },
    },
  });
});

beforeEach(async () => {
  await i18n.changeLanguage("en");
});

const wrapperAt = (path: string) => {
  const wrapper = ({ children }: PropsWithChildren) => (
    <BaseWrapper>
  return wrapper;
};

describe("Nav landmark", () => {
  it.each([
    { language: "en", name: "Navigation" },
    { language: "zh-TW", name: "導覽" },
  ])("exposes a translated navigation landmark in $language", async ({ language, name }) => {
    await i18n.changeLanguage(language);
    render(<Nav />, { wrapper: wrapperAt("/") });

    expect(screen.getByRole("navigation", { name })).toBeInTheDocument();
  });
});

describe("Nav dashboard button", () => {
  it("links to the dashboard at /home", () => {
    render(<Nav />, { wrapper: wrapperAt("/") });
